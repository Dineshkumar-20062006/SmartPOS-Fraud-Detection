from datetime import datetime
from decimal import Decimal
from database import SessionLocal
from models import Bill, BillItem, Product


def create_bill(
    cart_items,
    bill_no,
    paid_amount,
    payment_method="Cash"
):
    session = SessionLocal()

    try:
        valid_methods = ["Cash", "Card", "UPI"]
        if payment_method not in valid_methods:
            payment_method = "Cash"

        total_amount = Decimal("0.00")
        paid_dec = Decimal(str(paid_amount))
        bill_items = []

        if not cart_items:
            raise ValueError("Cart is empty")

        # Process cart items
        for item in cart_items:
            product = (
                session.query(Product)
                .filter(Product.id == item["product_id"])
                .first()
            )

            if product is None:
                raise ValueError(f"Product ID {item['product_id']} not found")

            if not product.is_active:
                raise ValueError(f"Product '{product.name}' is no longer active")

            qty = int(item["quantity"])
            if qty <= 0:
                raise ValueError(f"Invalid quantity {qty} for product {product.name}")

            if product.stock < qty:
                raise ValueError(f"Insufficient stock for {product.name} (Available: {product.stock})")

            unit_price = Decimal(str(product.price))
            subtotal = unit_price * qty
            total_amount += subtotal

            # Reduce stock
            product.stock -= qty

            bill_item = BillItem(
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price,
                subtotal=subtotal
            )
            bill_items.append(bill_item)

        # Payment validation
        if paid_dec < total_amount:
            raise ValueError(f"Payment amount (${paid_dec:.2f}) is less than total amount (${total_amount:.2f})")

        change_amount = paid_dec - total_amount
        now = datetime.now()

        bill = Bill(
            bill_no=bill_no,
            bill_date=now.date(),
            bill_time=now.time(),
            total_amount=total_amount,
            paid_amount=paid_dec,
            change_amount=change_amount,
            payment_method=payment_method
        )

        bill.items = bill_items

        session.add(bill)
        session.commit()
        session.refresh(bill)

        for item in bill.items:
            _ = item.product

        return bill

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()