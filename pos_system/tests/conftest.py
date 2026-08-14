import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, SessionLocal
from models import Product, Bill, BillItem


@pytest.fixture(autouse=True)
def setup_test_database(monkeypatch):
    test_engine = create_engine("sqlite:///:memory:")
    TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    Base.metadata.create_all(bind=test_engine)

    # Patch SessionLocal across database module and services
    monkeypatch.setattr("database.SessionLocal", TestSession)
    monkeypatch.setattr("services.product_service.SessionLocal", TestSession)
    monkeypatch.setattr("services.billing_service.SessionLocal", TestSession)
    monkeypatch.setattr("services.bill_number_service.SessionLocal", TestSession)
    monkeypatch.setattr("services.bill_history_service.SessionLocal", TestSession)

    yield TestSession

    Base.metadata.drop_all(bind=test_engine)
