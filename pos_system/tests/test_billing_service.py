from decimal import Decimal
import pytest
from services.product_service import add_product, get_all_products
from services.billing_service import create_bill
from services.bill_number_service import generate_bill_number


def test_create_bill_success():
    p1 = add_product("Chocolate", "4.50", 20)
    p2 = add_product("Juice", "2.00", 15)

    cart = [
        {"product_id": p1.id, "quantity": 2},
        {"product_id": p2.id, "quantity": 3}
    ]

    bill_no = generate_bill_number()
    bill = create_bill(cart, bill_no, Decimal("20.00"), "Cash")

    assert bill.bill_no == "1000000001"
    assert bill.total_amount == Decimal("15.00") # (4.50*2) + (2.00*3) = 9.00 + 6.00 = 15.00
    assert bill.paid_amount == Decimal("20.00")
    assert bill.change_amount == Decimal("5.00")
    assert bill.payment_method == "Cash"
    assert len(bill.items) == 2

    # Stock should be deducted
    products = {p.id: p for p in get_all_products()}
    assert products[p1.id].stock == 18
    assert products[p2.id].stock == 12


def test_create_bill_insufficient_payment():
    p1 = add_product("Coffee", "10.00", 5)
    cart = [{"product_id": p1.id, "quantity": 1}]
    bill_no = generate_bill_number()

    with pytest.raises(ValueError, match="Payment amount .* is less than total amount"):
        create_bill(cart, bill_no, Decimal("5.00"), "Cash")


def test_create_bill_insufficient_stock():
    p1 = add_product("Tea", "5.00", 2)
    cart = [{"product_id": p1.id, "quantity": 5}]
    bill_no = generate_bill_number()

    with pytest.raises(ValueError, match="Insufficient stock"):
        create_bill(cart, bill_no, Decimal("50.00"), "Cash")
