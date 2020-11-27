from django.shortcuts import render, redirect
from django.db import connection
import home.views as home_views


def load_orders(request):

    if not ('customer_id' in request.session):
        return render(request, 'purchases.html')

    cid = request.session['customer_id']
    cid = str(cid)

    # search btn pressed
    if request.method == 'POST' and 'search-btn' in request.POST:
        keywords = request.POST['search']
        keywords = str(keywords)
        return home_views.load_search_result(request, keywords)

    cursor = connection.cursor()

    # gets a list of purchase dates
    sql = "SELECT DISTINCT PURCHASE_DATE FROM TRANSACTION WHERE CUSTOMER_ID = " + str(cid) + ";"
    cursor.execute(sql)
    dates = cursor.fetchall()
    product_dict = []

    for date in dates:
        date = str(date[0])

        # ei date e ki ki bought
        sql = """SELECT * FROM TRANSACTION 
                WHERE CUSTOMER_ID = '""" + cid + """'
                AND PURCHASE_DATE = '""" + date + "';"

        cursor.execute(sql)
        table = cursor.fetchall()

        dictionary = []

        for data in table:
            product_id = data[2]
            quantity = data[3]
            payment_method = data[4]
            purchase_date = data[5]

            if payment_method == "COD":
                payment_method = "Cash on Delivery"
            else:
                payment_method = "Bank A/C"

            sql = "SELECT PRICE, NAME FROM PRODUCT WHERE PRODUCT_ID = " + str(product_id) + ";"
            cursor.execute(sql)
            table = cursor.fetchall()

            price = [x[0] for x in table]
            price = str(price[0])

            name = [x[1] for x in table]
            name = str(name[0])

            row = {'price': price, 'quantity': quantity, 'name': name,
                   'payment_method': payment_method, 'purchase_date': purchase_date}
            dictionary.append(row)

        # list of dictionaries, each list item contains ek date er all products
        product_dict.append(dictionary)

    sql = "SELECT EMAIL FROM CUSTOMER WHERE CUSTOMER_ID = " + cid
    cursor.execute(sql)
    name_table = cursor.fetchall()
    username = [data[0] for data in name_table]
    username = str(username[0])

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
    categories = cursor.fetchall()
    category_dict = []
    for r in categories:
        category = r[0]
        row = {'category': category}
        category_dict.append(row)

    return render(request, 'purchases.html', {'products_list': product_dict, 'username': username,
                                              'categories': category_dict})
