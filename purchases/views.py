from django.shortcuts import render, redirect
from django.db import connection
import home.views as home_views


def load_orders(request):

    if not ('customer_id' in request.session):
        return render(request, 'purchases.html')

    cid = request.session['customer_id']
    cid = str(cid)

    cart_item_no = ""
    if 'cart' in request.session:
        my_cart = request.session['cart']
        if len(my_cart) > 0:
            cart_item_no = "(" + str(len(my_cart)) + ")"

    # search btn pressed
    if request.method == 'POST' and 'search-btn' in request.POST:
        keywords = request.POST['search']
        keywords = str(keywords)
        return home_views.load_search_result(request, keywords)

    cursor = connection.cursor()

    # gets list of purchases with product names ordered by newest bought
    sql = """SELECT p.NAME, t.PRICE, t.QUANTITY, t.PAYMENT_METHOD, t.PURCHASE_DATE, t.GIFT_FOR
             FROM "THE_BAZAAR".PRODUCT p, "THE_BAZAAR".TRANSACTION t
             WHERE p.PRODUCT_ID = t.PRODUCT_ID AND t.CUSTOMER_ID = """ + cid + """ 
             ORDER BY t.PURCHASE_DATE DESC;"""
    cursor.execute(sql)
    data_table = cursor.fetchall()
    product_dict = []
    dictionary = []

    length = len(data_table)
    for index, data in enumerate(data_table):

        name = data[0]
        price = data[1]
        quantity = data[2]
        payment_method = data[3]
        purchase_date = data[4]
        gift = data[5]

        if gift != "NULL":
            gift = "Gift To: " + gift
        else:
            gift = ""

        if payment_method == "COD":
            payment_method = "Cash on Delivery"
        else:
            payment_method = "Bank A/C"

        row = {'price': price, 'quantity': quantity, 'name': name, 'gift': gift,
               'payment_method': payment_method, 'purchase_date': purchase_date}
        dictionary.append(row)

        # This condition makes sure that purchases of the
        # same date are displayed together
        # if next-row exists, check if purchase date matches
        # if date does not match, append the "list-of-dict" and empty it!
        if index < (length - 1):
            next_row = data_table[index + 1]
            if purchase_date != next_row[4]:
                product_dict.append(dictionary)
                dictionary = []
        # append the last
        if index == length - 1:
            product_dict.append(dictionary)


    # username display
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

    sql = """SELECT OFFER_ID FROM PRODUCT WHERE OFFER_ID IS NOT NULL;"""
    cursor.execute(sql)
    temp = cursor.fetchall()
    if cursor.rowcount > 0:
        row = {'category': "Discounts"}
        category_dict.append(row)

    return render(request, 'purchases.html', {'products_list': product_dict, 'username': username,
                                              'categories': category_dict, 'items_len': cart_item_no})
