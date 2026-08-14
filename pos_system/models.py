from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Date,
    Time,
    ForeignKey,
    DateTime,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database import Base


# =========================
# Product Table
# =========================

class Product(Base):

    __tablename__ = "products"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )


    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )


    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )


    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )


    # Relationship with BillItem

    bill_items = relationship(
        "BillItem",
        back_populates="product"
    )



# =========================
# Bill Table
# =========================

class Bill(Base):

    __tablename__ = "bills"


    # 10 digit unique bill number

    bill_no: Mapped[str] = mapped_column(
        String(10),
        primary_key=True
    )


    bill_date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )


    bill_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False
    )


    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )


    # Payment Information

    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )


    change_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )


    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Cash"
    )


    # Relationship with BillItem

    items = relationship(
        "BillItem",
        back_populates="bill",
        cascade="all, delete"
    )



# =========================
# Bill Items Table
# =========================

class BillItem(Base):

    __tablename__ = "bill_items"



    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )



    bill_no: Mapped[str] = mapped_column(
        ForeignKey("bills.bill_no"),
        nullable=False,
        index=True
    )



    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )



    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )



    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )



    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )



    # Relationship with Bill

    bill = relationship(
        "Bill",
        back_populates="items"
    )



    # Relationship with Product

    product = relationship(
        "Product",
        back_populates="bill_items"
    )