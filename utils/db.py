def insert_into_db(client, DATA):

    db = client.products
    products = db.products

    for data in DATA:
        products.insert_one(data)
