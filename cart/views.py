from django.shortcuts import render, redirect
from login.views import load_login
from django.db import connection
from datetime import datetime
import home.views as homeviews


def get_cart_list(cart_list):
    cursor = connection.cursor()
    detailed_list = []
    total = 0
    items = 0
    can_check_out = True

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

        stock = cursor.callfunc('IS_IN_STOCK', str, [pid, quantity])

        if stock != "NO":
            stock = "available"
        else:
            stock = ""
            if can_check_out:
                can_check_out = False

        disc = cursor.callfunc('HAS_DISCOUNT', str, [pid])
        if disc != "NO":
            perc = int(disc)
            price = int(price)*((100-perc)/100)
            price_text = str(price) + " (after -" + str(perc) + "%)"

        total += int(price) * int(quantity)
        items += int(quantity)
        detailed_list.append({'name': name, 'price': price_text,
                              'quantity': quantity, 'product_id': pid, 'stock': stock})

    cursor.close()
    return detailed_list, total, items, can_check_out


def check_stock_before_buy(request):
    if 'cart' in request.session:
        cursor = connection.cursor()
        cart_list = request.session['cart']
        for cart in cart_list:
            pid = str(cart['product_id'])
            quan = str(cart['quantity'])

            stock = cursor.callfunc('IS_IN_STOCK', str, [pid, quan])
            if stock == "NO":
                return False
        return True
    return True


def load_cart(request):

    # send to login if no session exists:
    if not('customer_id' in request.session):
        return redirect(load_login)

    cart_item_no = ""
    if 'cart' in request.session:
        my_cart = request.session['cart']
        if len(my_cart) > 0:
            cart_item_no = "(" + str(len(my_cart)) + ")"

    # buy btn pressed:
    if request.method == 'POST' and 'buy-btn' in request.POST:
        payment = str(request.POST['payment'])
        gift_for = str(request.POST['gift'])
        cart_item_no = ""
        if check_stock_before_buy(request):
            check_out(payment, gift_for, request)
        else:
            return redirect(load_cart)


    # search btn pressed
    if request.method == 'POST' and 'search-btn' in request.POST:
        keywords = request.POST['search']
        keywords = str(keywords)
        return homeviews.load_search_result(request, keywords)

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

    sql = """SELECT OFFER_ID FROM PRODUCT WHERE OFFER_ID IS NOT NULL;"""
    cursor.execute(sql)
    temp = cursor.fetchall()
    if cursor.rowcount > 0:
        row = {'category': "Discounts"}
        cat_dict.append(row)

    cursor.close()
    cart_list = []

    # total price of items in cart
    total = 0
    items = 0
    if 'cart' in request.session:
        cart_list = request.session['cart']
        cart_list, total, items, can_check_out = get_cart_list(cart_list)
        if can_check_out:
            can_check_out = "yes"
        else:
            can_check_out = ""
        return render(request, "cart.html", {'username': username, 'categories': cat_dict, 'can_buy': can_check_out,
                                             'cart': cart_list, 'total_price': total, 'total_items': items,
                                             'items_len': cart_item_no})
    else:
        return render(request, "cart.html", {'username': username, 'categories': cat_dict,
                                             'cart': cart_list, 'total_price': total, 'total_items': items,
                                             'items_len': cart_item_no})


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


def check_out(payment, gift_for, request):
    if 'cart' in request.session:
        cursor = connection.cursor()
        cart_list = request.session['cart']

        c_id = str(request.session['customer_id'])
        employee_id = cursor.callfunc('GET_DELIVERY_MAN', str)
        purchase_date = str(datetime.now().replace(microsecond=0))
        transaction_id = int(cursor.callfunc('GET_TRANSACTION_ID', str))
        transaction_id += 1

        if gift_for == "":
            gift_for = "NULL"
        # TO_DATE('2020-11-28 18:13:09', 'YYYY-MM-DD HH24:MI:SS')

        for item in cart_list:
            pid = str(item['product_id'])
            quan = str(item['quantity'])

            sql = "SELECT PRICE FROM PRODUCT WHERE PRODUCT_ID = " + pid + ";"
            cursor.execute(sql)
            table = cursor.fetchall()
            price = [data[0] for data in table]
            price = str(price[0])

            disc = cursor.callfunc('HAS_DISCOUNT', str, [pid])
            if disc != "NO":
                perc = int(disc)
                price = int(price) * ((100 - perc) / 100)
                price = str(price)

            sql = """INSERT INTO TRANSACTION (TRANSACTION_ID, CUSTOMER_ID, 
            PRODUCT_ID, QUANTITY, PAYMENT_METHOD, PURCHASE_DATE, EMPLOYEE_ID, PRICE, GIFT_FOR)
            VALUES (""" + str(transaction_id) + "," + c_id + "," + pid + "," + quan + ",'" + payment + "'," + """
            TO_DATE('""" + purchase_date + "', 'YYYY-MM-DD HH24:MI:SS')" + "," + employee_id + """
            ,""" + price + ",'" + gift_for + "');"

            transaction_id += 1
            cursor.execute(sql)

        request.session['cart'] = ""
        del request.session['cart']
        return redirect(load_cart)
