from decimal import Decimal
from services.product_service import add_product
from services.billing_service import create_bill
from services.bill_number_service import generate_bill_number


def test_bill_number_sequence():
    b_no1 = generate_bill_number()
    assert b_no1 == "1000000001"

    p = add_product("Soda", "1.50", 100)
    cart = [{"product_id": p.id, "quantity": 1}]
    create_bill(cart, b_no1, Decimal("5.00"), "Cash")

    b_no2 = generate_bill_number()
    assert b_no2 == "1000000002"
