import os
import sys
import threading # <-- NEW
import requests
from datetime import datetime, date, time
from decimal import Decimal
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_tables import create_tables
from services.product_service import (
    get_all_products,
    search_products,
    get_low_stock_products,
    add_product,
    update_product,
    delete_product
)
from services.bill_number_service import generate_bill_number
from services.billing_service import create_bill
from services.bill_history_service import (
    get_all_bills,
    search_bill,
    get_sales_analytics
)
from services.receipt_service import generate_receipt, generate_pdf_receipt

# Ensure database tables exist
create_tables()

# Setup Flask application
web_ui_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_ui", "dist")
app = Flask(__name__, static_folder=web_ui_dist, static_url_path="")
CORS(app)


# Helper serializer
def serialize_model(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    return obj


def dispatch_to_billguard_async(bill_no, bill_date):
    """
    Sends POS data to BillGuard AI securely in a background thread 
    so the cashier UI does not experience any lag.
    """
    def _send():
        # Format date as DD/MM/YYYY to perfectly match your OCR Regex
        formatted_date = bill_date.strftime('%d/%m/%Y')
        payload = {
            "bill_number": str(bill_no),
            "date": formatted_date
        }
        try:
            # BillGuard AI is running on port 5000
            response = requests.post("http://127.0.0.1:5000/api/pos/issue-bill", json=payload, timeout=3.0)
            print(f"[BillGuard Integration] Bill {bill_no} secured. Status: {response.status_code}")
        except Exception as e:
            print(f"[BillGuard Integration] Failed to reach BillGuard server: {e}")

    # Fire and forget thread
    threading.Thread(target=_send, daemon=True).start()



def product_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "price": float(p.price),
        "stock": p.stock,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None
    }


def bill_item_to_dict(item):
    return {
        "id": item.id,
        "bill_no": item.bill_no,
        "product_id": item.product_id,
        "product_name": item.product.name if item.product else f"Product #{item.product_id}",
        "quantity": item.quantity,
        "unit_price": float(item.unit_price),
        "subtotal": float(item.subtotal)
    }


def bill_to_dict(b, include_items=False):
    res = {
        "bill_no": b.bill_no,
        "bill_date": b.bill_date.isoformat() if b.bill_date else None,
        "bill_time": b.bill_time.isoformat() if b.bill_time else None,
        "total_amount": float(b.total_amount),
        "paid_amount": float(b.paid_amount),
        "change_amount": float(b.change_amount),
        "payment_method": b.payment_method
    }
    if include_items:
        res["items"] = [bill_item_to_dict(item) for item in b.items]
    return res


# ==================== PRODUCT ENDPOINTS ====================

@app.route("/api/products", methods=["GET"])
def api_get_products():
    include_inactive = request.args.get("include_inactive", "false").lower() == "true"
    query = request.args.get("search", "").strip()

    if query:
        products = search_products(query, include_inactive=include_inactive)
    else:
        products = get_all_products(include_inactive=include_inactive)

    return jsonify([product_to_dict(p) for p in products])


@app.route("/api/products/low-stock", methods=["GET"])
def api_get_low_stock():
    threshold = int(request.args.get("threshold", 10))
    products = get_low_stock_products(threshold=threshold)
    return jsonify([product_to_dict(p) for p in products])


@app.route("/api/products", methods=["POST"])
def api_add_product():
    data = request.json or {}
    try:
        name = data.get("name")
        price = data.get("price")
        stock = data.get("stock")

        new_product = add_product(name, price, stock)
        return jsonify({"success": True, "product": product_to_dict(new_product)}), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"Failed to add product: {str(err)}"}), 500


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def api_update_product(product_id):
    data = request.json or {}
    try:
        name = data.get("name")
        price = data.get("price")
        stock = data.get("stock")

        updated = update_product(product_id, name, price, stock)
        return jsonify({"success": True, "product": product_to_dict(updated)})
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"Failed to update product: {str(err)}"}), 500


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    try:
        success = delete_product(product_id)
        if success:
            return jsonify({"success": True, "message": "Product deactivated successfully"})
        return jsonify({"error": "Product not found"}), 404
    except Exception as err:
        return jsonify({"error": f"Failed to delete product: {str(err)}"}), 500


# ==================== BILLING ENDPOINTS ====================

@app.route("/api/bill/next-number", methods=["GET"])
def api_next_bill_number():
    bill_no = generate_bill_number()
    return jsonify({"bill_no": bill_no})


@app.route("/api/bill/checkout", methods=["POST"])
def api_checkout():
    data = request.json or {}
    try:
        cart_items = data.get("cart_items", [])
        bill_no = data.get("bill_no") or generate_bill_number()
        paid_amount = data.get("paid_amount", 0)
        payment_method = data.get("payment_method", "Cash")

        bill = create_bill(
            cart_items=cart_items,
            bill_no=bill_no,
            paid_amount=paid_amount,
            payment_method=payment_method
        )

        # Generate txt receipt file automatically
        txt_path = generate_receipt(bill)

        # ---> NEW: TRIGGER THE BILLGUARD AI WEBHOOK <---
        dispatch_to_billguard_async(bill.bill_no, bill.bill_date)

        return jsonify({
            "success": True,
            "bill": bill_to_dict(bill, include_items=True),
            "receipt_path": txt_path
        }), 201

    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        return jsonify({"error": f"Checkout failed: {str(err)}"}), 500


@app.route("/api/bills", methods=["GET"])
def api_get_bills():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None

    bills = get_all_bills(start_date=start_date, end_date=end_date)
    return jsonify([bill_to_dict(b) for b in bills])


@app.route("/api/bills/<bill_no>", methods=["GET"])
def api_get_bill_detail(bill_no):
    bill = search_bill(bill_no)
    if not bill:
        return jsonify({"error": "Bill not found"}), 404
    return jsonify(bill_to_dict(bill, include_items=True))


@app.route("/api/analytics", methods=["GET"])
def api_get_analytics():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None

    stats = get_sales_analytics(start_date=start_date, end_date=end_date)
    return jsonify({
        "total_revenue": float(stats["total_revenue"]),
        "total_bills": stats["total_bills"],
        "avg_bill": float(stats["avg_bill"]),
        "payment_breakdown": {
            k: float(v) for k, v in stats["payment_breakdown"].items()
        }
    })


@app.route("/api/bills/<bill_no>/receipt", methods=["GET"])
def api_get_receipt(bill_no):
    fmt = request.args.get("format", "txt").lower()
    bill = search_bill(bill_no)
    if not bill:
        return jsonify({"error": "Bill not found"}), 404

    if fmt == "pdf":
        pdf_path = generate_pdf_receipt(bill)
        if os.path.exists(pdf_path) and pdf_path.endswith(".pdf"):
            return send_file(pdf_path, mimetype="application/pdf", as_attachment=False)
        # Fallback if pdf built txt instead
        txt_path = generate_receipt(bill)
        return send_file(txt_path, mimetype="text/plain", as_attachment=False)
    else:
        txt_path = generate_receipt(bill)
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"bill_no": bill_no, "receipt_text": content})


# ==================== FRONTEND STATIC SERVING ====================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_file = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({"message": "ABC Supermarket POS Backend API is running. React frontend static build not found yet."}), 200


if __name__ == "__main__":
    # Change port from 5000 to 5001
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting ABC Supermarket POS API Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)