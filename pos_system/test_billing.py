from services.billing_service import create_bill
from services.bill_number_service import generate_bill_number


cart = [
    {
        "product_id": 1,
        "quantity": 2
    },
    {
        "product_id": 2,
        "quantity": 3
    }
]


bill_no = generate_bill_number()
bill = create_bill(cart, bill_no, 100.0, "Cash")


print("Bill Number:", bill.bill_no)
print("Total:", bill.total_amount)