from decimal import Decimal
from database import SessionLocal
from models import Bill, BillItem
from sqlalchemy.orm import joinedload


def get_all_bills(start_date=None, end_date=None):
    session = SessionLocal()
    try:
        query = session.query(Bill)
        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)
        bills = query.order_by(Bill.bill_date.desc(), Bill.bill_no.desc()).all()
        return bills
    finally:
        session.close()


def search_bill(bill_no):
    session = SessionLocal()
    try:
        bill = (
            session.query(Bill)
            .options(
                joinedload(Bill.items)
                .joinedload(BillItem.product)
            )
            .filter(
                Bill.bill_no == bill_no
            )
            .first()
        )
        return bill
    finally:
        session.close()


def get_sales_analytics(start_date=None, end_date=None):
    session = SessionLocal()
    try:
        query = session.query(Bill)
        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)

        bills = query.all()
        total_revenue = Decimal("0.00")
        total_bills = len(bills)
        payment_breakdown = {"Cash": Decimal("0.00"), "Card": Decimal("0.00"), "UPI": Decimal("0.00")}

        for b in bills:
            amt = Decimal(str(b.total_amount))
            total_revenue += amt
            method = b.payment_method if b.payment_method in payment_breakdown else "Cash"
            payment_breakdown[method] += amt

        avg_bill = (total_revenue / total_bills) if total_bills > 0 else Decimal("0.00")

        return {
            "total_revenue": total_revenue,
            "total_bills": total_bills,
            "avg_bill": avg_bill,
            "payment_breakdown": payment_breakdown
        }
    finally:
        session.close()