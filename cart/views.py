from django.shortcuts import render, redirect
from login.views import load_login
from django.db import connection


def get_cart_list(cart_list):
    cursor = connection.cursor()
    detailed_list = []
    total = 0
    items = 0

    for cart in cart_list:
        pid = cart['product_id']
        pid = str(pid)
        quantity = cart['quantity']

        sql = """SELECT NAME, PRICE FROM PRODUCT
         WHERE PRODUCT_ID = '""" + pid + """';"""

        cursor.execute(sql)
        data_table = cursor.fetchall()
        name = [data[0] for data in data_table]
        price = [data[1] for data in data_table]
        name = str(name[0])
        price = str(price[0])
        price_text = price

        disc = cursor.callfunc('HAS_DISCOUNT', str, [pid])
        if disc != "NO":
            perc = int(disc)
            price = int(price)*((100-perc)/100)
            price_text = str(price) + " (after -" + str(perc) + "%)"

        total += int(price) * int(quantity)
        items += int(quantity)
        detailed_list.append({'name': name, 'price': price_text, 'quantity': quantity, 'product_id': pid})

    cursor.close()
    return detailed_list, total, items


def load_cart(request):

    # send to login if no session exists:
    if not('customer_id' in request.session):
        return redirect(load_login)

    cursor = connection.cursor()
    customer_id = request.session.get('customer_id')
    customer_id = str(customer_id)
    sql = "SELECT EMAIL FROM CUSTOMER WHERE CUSTOMER_ID = " + customer_id
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
    table = cursor.fetchall()
    cat_dict = []

    for r in table:
        category = r[0]
        row = {'category': category}
        cat_dict.append(row)

    cursor.close()
    cart_list = []

    # total price of items in cart
    total = 0
    items = 0
    if 'cart' in request.session:
        cart_list = request.session['cart']
        cart_list, total, items = get_cart_list(cart_list)
        return render(request, "cart.html", {'username': username, 'categories': cat_dict,
                                             'cart': cart_list, 'total_price': total, 'total_items': items})
    else:
        return render(request, "cart.html", {'username': username, 'categories': cat_dict,
                                             'cart': cart_list, 'total_price': total, 'total_items': items})


def del_cart_item(request, slug):
    if 'cart' in request.session:
        cart_list = request.session['cart']
        new_list = []
        for cart in cart_list:
            if str(cart['product_id']) == str(slug):
                continue
            new_list.append(cart)
        del request.session['cart']
        request.session['cart'] = new_list
    return redirect(load_cart)

