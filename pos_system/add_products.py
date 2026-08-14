from database import SessionLocal
from models import Product


def add_products():

    session = SessionLocal()

    try:

        products = [

            Product(
                name="Rice",
                price=15.00,
                stock=100
            ),

            Product(
                name="Milk",
                price=4.00,
                stock=50
            ),

            Product(
                name="Bread",
                price=3.00,
                stock=40
            ),

            Product(
                name="Sugar",
                price=5.00,
                stock=80
            ),

            Product(
                name="Tea Powder",
                price=10.00,
                stock=60
            )

        ]


        session.add_all(products)

        session.commit()


        print("Products added successfully")


    except Exception as e:

        session.rollback()

        print(e)


    finally:

        session.close()



if __name__ == "__main__":

    add_products()