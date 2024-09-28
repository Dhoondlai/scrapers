from datetime import datetime


def insert_into_db(client, DATA, vendor_name):
    db = client.dhoondlai
    products = db.products

    # Set all products of this vendor as inactive (available=False)
    try:
        products.update_many({"vendor": vendor_name}, {
            "$set": {"available": False}})
        print(f"Set all products of vendor '{vendor_name}' as inactive.")
    except Exception as e:
        print(f"Error while updating products: {e}")

    print("Inserting data into database")
    print("Total products to insert: ", len(DATA))
    count = 0
    for data in DATA:
        count += 1
        print(f"Inserting product {count}/{len(DATA)}")
        # Check if the product exists based on name and vendor
        try:
            existing_product = products.find_one(
                {"name": data['name'], "vendor": data['vendor']})

            if existing_product:
                # Update the product but keep the created_at timestamp unchanged
                result = products.update_one(
                    {"_id": existing_product['_id']},
                    {"$set": {
                        "price_low": data.get('price_low', existing_product['price_low']),
                        "price_high": data.get('price_high', existing_product['price_high']),
                        "updated_at": datetime.now(),
                        "warranty": data.get('warranty', existing_product.get('warranty')),
                        "category": data.get('category', existing_product.get('category')),
                        "link": data['link'],
                        "available": True
                    }}
                )
                if result.modified_count > 0:
                    print(
                        f"Updated existing product: {data['name']} (Vendor: {vendor_name})")
                else:
                    print(
                        f"No changes made to existing product: {data['name']} (Vendor: {vendor_name})")
            else:
                # Insert new product if it doesn't exist
                data['created_at'] = datetime.now()
                data['updated_at'] = datetime.now()
                result = products.insert_one(data)
                print(
                    f"Inserted new product: {data['name']} (Vendor: {vendor_name}) with ID: {result.inserted_id}")
        except Exception as e:
            print(f"Error processing product '{data['name']}': {e}")
