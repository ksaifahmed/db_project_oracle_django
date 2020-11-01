from django.shortcuts import render, redirect
from django.db import connection
from login.views import load_login


def load_product(request, slug):

    # send to login if no session exists:
    if not('customer_id' in request.session):
        return redirect(load_login)

    cursor = connection.cursor()
    sql = """SELECT p.PRODUCT_ID, p.NAME, p.CATEGORY, p.BRAND, p.PRICE, p.DESCRIPTION, o.DESCRIPTION AS DISCOUNT, p.IMAGE_LINK, s.quantity
            FROM THE_BAZAAR.PRODUCT p, THE_BAZAAR.OFFER o, THE_BAZAAR.STOCK s
            WHERE p.OFFER_ID = o.OFFER_ID(+)
            AND p.PRODUCT_ID = s.PRODUCT_ID
            AND p.PRODUCT_ID = """ + slug + """;"""
    cursor.execute(sql)
    table = cursor.fetchall()
    product_dict = []
    for r in table:
        id = r[0]
        name = r[1]
        category = r[2]
        brand = r[3]
        price = r[4]
        description = r[5]
        discount = r[6]
        image_link = r[7]
        quantity_left = r[8]
        row = {
            'id': id, 'name': name, 'category': category, 'brand': brand, 'price': price,
            'description': description, 'discount': discount, 'image_link': image_link, 'quantity_left': quantity_left
            }
        product_dict = row

    sql = """SELECT DISTINCT CATEGORY
            FROM PRODUCT
            WHERE PRODUCT_ID = ANY(
                SELECT PRODUCT_ID 
                FROM STOCK 
                WHERE EXPIRE_DATE > SYSDATE AND QUANTITY > 0

            UNION

                SELECT PRODUCT_ID
                FROM STOCK WHERE
                EXPIRE_DATE IS NULL AND QUANTITY > 0
            );"""

    cursor.execute(sql)
    table = cursor.fetchall()
    cat_dict = []

    for r in table:
        category = r[0]
        row = {'category': category}
        cat_dict.append(row)

    #cursor.close()

    q_dict = []

    if request.method == 'POST':
        data = request.POST['quantity']
        quantity = {'quantity': data}
        q_dict = quantity

    cursor.close()

    return render(request, 'productpage.html', {'product': product_dict, 'categories': cat_dict, 'quantity_selected': q_dict})
