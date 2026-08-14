from database import SessionLocal
from models import Bill

STARTING_BILL_NO = 1000000000


def generate_bill_number():
    session = SessionLocal()
    try:
        # Fetch all bill numbers or latest to find numeric max safely
        bills = session.query(Bill.bill_no).all()
        if not bills:
            next_number = STARTING_BILL_NO + 1
        else:
            max_num = STARTING_BILL_NO
            for (b_no,) in bills:
                try:
                    num = int(b_no)
                    if num > max_num:
                        max_num = num
                except (ValueError, TypeError):
                    continue
            next_number = max_num + 1

        return str(next_number).zfill(10)
    finally:
        session.close()