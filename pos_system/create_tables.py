from database import engine, Base

# Import models so SQLAlchemy knows about them
from models import Product, Bill, BillItem


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()