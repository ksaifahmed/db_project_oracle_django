from django.shortcuts import render
from django.db import connection


def load_product(request, slug):
    cursor = connection.cursor()
    print(id)
    sql = "SELECT * FROM PRODUCT WHERE PRODUCT_ID = " + slug
    cursor.execute(sql)
    table = cursor.fetchall()
    product_dict = []
    for r in table:
        #id = r[0]
        name = r[1]
        category = r[2]
        brand = r[3]
        price = r[4]
        description = r[5]
        offer_id = r[6]
        image_link = r[7]
        row = {
            'name': name, 'category': category, 'brand': brand, 'price': price,
            'description': description, 'offer_id': offer_id, 'image_link': image_link
            }
        product_dict = row

    sql = "SELECT DISTINCT CATEGORY FROM PRODUCT"
    cursor.execute(sql)
    table = cursor.fetchall()
    cat_dict = []

    for r in table:
        category = r[0]
        row = {'category': category}
        cat_dict.append(row)

    cursor.close()

    return render(request, 'productpage.html', {'product': product_dict, 'categories': cat_dict})