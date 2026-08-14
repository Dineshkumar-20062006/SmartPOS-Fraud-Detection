from decimal import Decimal
from database import SessionLocal
from models import Product


def get_all_products(include_inactive=False):
    session = SessionLocal()
    try:
        query = session.query(Product)
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        products = query.order_by(Product.id).all()
        return products
    finally:
        session.close()


def search_products(query_text, include_inactive=False):
    session = SessionLocal()
    try:
        query = session.query(Product)
        if not include_inactive:
            query = query.filter(Product.is_active == True)

        if query_text:
            search_pattern = f"%{query_text.strip()}%"
            query = query.filter(Product.name.ilike(search_pattern))

        return query.order_by(Product.name).all()
    finally:
        session.close()


def get_low_stock_products(threshold=10):
    session = SessionLocal()
    try:
        return (
            session.query(Product)
            .filter(Product.is_active == True, Product.stock <= threshold)
            .order_by(Product.stock.asc())
            .all()
        )
    finally:
        session.close()


def add_product(name, price, stock):
    session = SessionLocal()
    try:
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")

        price_dec = Decimal(str(price))
        if price_dec <= Decimal("0"):
            raise ValueError("Price must be greater than zero")

        stock_int = int(stock)
        if stock_int < 0:
            raise ValueError("Stock cannot be negative")

        product = Product(
            name=name.strip(),
            price=price_dec,
            stock=stock_int,
            is_active=True
        )

        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_product(product_id, name, price, stock):
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise ValueError("Product not found")

        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")

        price_dec = Decimal(str(price))
        if price_dec <= Decimal("0"):
            raise ValueError("Price must be greater than zero")

        stock_int = int(stock)
        if stock_int < 0:
            raise ValueError("Stock cannot be negative")

        product.name = name.strip()
        product.price = price_dec
        product.stock = stock_int

        session.commit()
        session.refresh(product)
        return product
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_product(product_id):
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if product:
            product.is_active = False
            product.stock = 0
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()