from decimal import Decimal
import pytest
from services.product_service import (
    add_product,
    get_all_products,
    update_product,
    delete_product,
    search_products,
    get_low_stock_products
)


def test_add_and_get_product():
    p1 = add_product("Apple", "2.50", 50)
    assert p1.id is not None
    assert p1.name == "Apple"
    assert p1.price == Decimal("2.50")
    assert p1.stock == 50

    all_products = get_all_products()
    assert len(all_products) == 1
    assert all_products[0].name == "Apple"


def test_invalid_product_inputs():
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        add_product("", "2.50", 10)

    with pytest.raises(ValueError, match="Price must be greater than zero"):
        add_product("Orange", "-5.00", 10)

    with pytest.raises(ValueError, match="Stock cannot be negative"):
        add_product("Banana", "1.00", -5)


def test_update_product():
    p = add_product("Milk", "3.00", 20)
    updated = update_product(p.id, "Whole Milk", "3.50", 15)
    assert updated.name == "Whole Milk"
    assert updated.price == Decimal("3.50")
    assert updated.stock == 15


def test_soft_delete_product():
    p = add_product("Bread", "2.00", 30)
    result = delete_product(p.id)
    assert result is True

    active_products = get_all_products(include_inactive=False)
    assert len(active_products) == 0

    all_products = get_all_products(include_inactive=True)
    assert len(all_products) == 1
    assert all_products[0].is_active is False
    assert all_products[0].stock == 0


def test_search_and_low_stock():
    add_product("Basmati Rice", "12.00", 5)
    add_product("Brown Rice", "14.00", 50)
    add_product("Wheat Flour", "8.00", 8)

    rice_results = search_products("Rice")
    assert len(rice_results) == 2

    low_stock = get_low_stock_products(threshold=10)
    assert len(low_stock) == 2
    assert low_stock[0].stock <= 10
