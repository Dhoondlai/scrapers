import time


def insert_to_dynamodb(dynamodb, name, vendor, price, warranty, category, url):
    table = dynamodb.Table('products')

    # Step 1: Check if the product already exists for the same name and vendor
    response = table.get_item(
        Key={
            'name': name,
            'vendor': vendor
        }
    )

    if 'Item' in response:
        # Step 2: If product exists for this vendor, update any changed fields
        product = response['Item']

        # Update price range if needed
        price_low = min(int(product['price_low']), int(price))
        price_high = max(int(product['price_high']), int(price))

        # Update the item in DynamoDB
        table.update_item(
            Key={
                'name': name,
                'vendor': vendor
            },
            UpdateExpression="""
                SET price_low = :pl, price_high = :ph, updated_at = :ua, warranty = :w, category = :c, available = :av, url = :u
            """,
            ExpressionAttributeValues={
                ':pl': price_low,
                ':ph': price_high,
                ':ua': str(int(time.time())),
                ':w': warranty,
                ':c': category,
                ':av': True,
                ':u': url
            }
        )
    else:
        # Step 3: Check if the product exists with a different vendor
        response = table.query(
            KeyConditionExpression=Key('name').eq(name)
        )

        if response['Items']:
            # If it exists with a different vendor, reuse the description from the original product
            product = response['Items'][0]
            description = product.get('description', '')

            # Add the new product with the new vendor but reuse the description
            table.put_item(
                Item={
                    'name': name,
                    'vendor': vendor,
                    'price_low': int(price),
                    'price_high': int(price),
                    'updated_at': str(int(time.time())),
                    'created_at': str(int(time.time())),
                    'warranty': warranty,
                    'category': category,
                    'available': True,
                    'url': url,
                    'description': description
                }
            )
        else:
            # Step 4: If the product doesn't exist at all, add it as a new product
            table.put_item(
                Item={
                    'name': name,
                    'vendor': vendor,
                    'price_low': int(price),
                    'price_high': int(price),
                    'updated_at': str(int(time.time())),
                    'created_at': str(int(time.time())),
                    'warranty': warranty,
                    'category': category,
                    'available': True,
                    'url': url
                }
            )
