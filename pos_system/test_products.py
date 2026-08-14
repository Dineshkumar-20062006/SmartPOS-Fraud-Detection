from services.product_service import add_product, get_all_products


add_product(
    "Rice",
    15.00,
    100
)

add_product(
    "Milk",
    4.00,
    50
)

add_product(
    "Bread",
    3.00,
    80
)


products = get_all_products()


for product in products:
    print(
        product.id,
        product.name,
        product.price,
        product.stock
    )
    