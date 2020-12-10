from django.shortcuts import render, redirect
from django.db import connection
from login.views import load_login
import home.views as homeviews


def init_cart(pid, quan):
    item1 = {'product_id': pid, 'quantity': quan}
    cart = []
    cart.append(item1)
    return cart


def add_to_cart(pid, quan, cart):
    item = {'product_id': pid, 'quantity': quan}
    cart.append(item)
    return cart


def load_product(request, slug):

    # send to login if no session exists:
    if not('customer_id' in request.session):
        return redirect(load_login)

    cart_item_no = ""
    if 'cart' in request.session:
        my_cart = request.session['cart']
        if len(my_cart) > 0:
            cart_item_no = "(" + str(len(my_cart)) + ")"

    if request.method == 'POST' and 'search-btn' in request.POST:
        keywords = request.POST['search']
        keywords = str(keywords)
        return homeviews.load_search_result(request, keywords)

    cursor = connection.cursor()
    sql = """SELECT p.PRODUCT_ID, p.NAME, p.CATEGORY, p.BRAND, p.PRICE, p.DESCRIPTION, o.DESCRIPTION AS DISCOUNT, p.IMAGE_LINK, s.quantity, o.DISCOUNT_TYPE
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
        discount_desc = r[9]
        row = {
            'id': id, 'name': name, 'category': category, 'brand': brand, 'price': price,
            'description': description, 'discount': discount, 'image_link': image_link,
            'quantity_left': quantity_left, 'discount_desc': discount_desc
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


    sql = """SELECT OFFER_ID FROM PRODUCT WHERE OFFER_ID IS NOT NULL;"""
    cursor.execute(sql)
    temp = cursor.fetchall()
    if cursor.rowcount > 0:
        row = {'category': "Discounts"}
        cat_dict.append(row)

    customer_id = request.session.get('customer_id')
    customer_id = str(customer_id)
    sql = "SELECT EMAIL FROM CUSTOMER WHERE CUSTOMER_ID = " + customer_id
    cursor.execute(sql)
    name_table = cursor.fetchall()
    username = [data[0] for data in name_table]
    username = str(username[0])

    stock_info = ""
    pid = product_dict['id']
    in_stock = cursor.callfunc('IS_IN_STOCK', str, [pid, 1])
    in_stock = str(in_stock)
    if in_stock != "NO":
        stock_info = "available"

    # adding to cart
    if request.method == 'POST' and 'quantity-btn' in request.POST:
        data = request.POST['quantity']
        quantity = {'quantity': data}
        q_dict = quantity
        pid = product_dict['id']

        # IS_IN_STOCK pl-sql function checks whether at least 1 with valid exp_date is in stock
        in_stock = cursor.callfunc('IS_IN_STOCK', str, [pid, 1])
        in_stock = str(in_stock)

        if in_stock != "NO":
            stock_info = "available"

        if not ('cart' in request.session):
            request.session['cart'] = init_cart(pid, data)
            cart = request.session['cart']
            cart_item_no = len(cart)
            cart_item_no = "(" + str(cart_item_no) + ")"
        else:
            cart = request.session['cart']
            cart = add_to_cart(pid, data, cart)
            cart_item_no = len(cart)
            cart_item_no = "(" + str(cart_item_no) + ")"
            request.session['cart'] = cart

        return render(request, 'productpage.html', {'stock_info': stock_info, 'username': username, 'product': product_dict, 'categories': cat_dict, 'quantity_selected': q_dict, 'items_len': cart_item_no})

    cursor.close()
    return render(request, 'productpage.html', {'stock_info': stock_info, 'username': username, 'product': product_dict, 'categories': cat_dict, 'items_len': cart_item_no})
