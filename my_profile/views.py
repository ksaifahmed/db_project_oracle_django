from django.shortcuts import render, redirect
from django.db import connection
import hashlib
import login.views as login_views
import home.views as home_views


phone1 = 0
phone2 = 0
phone3 = 0
dictionary = []
phone_dict = []
category_dict = []
username = ""
msg = ""


def convert_number(number):
    if number == "":
        return number

    if number[0] == '0':
        num = int(number)
        num += 8800000000000
        num = str(num)
        return num
    else:
        return number


def keep_running_profile(request):
    global id
    global dictionary
    global phone_dict
    global category_dict
    global username
    global phone1
    global phone2
    global phone3
    global msg

    dictionary = []
    phone_dict = []

    id = request.session['customer_id']

    id = str(id)
    cursor = connection.cursor()
    sql = """SELECT CUSTOMER_ID,FIRST_NAME,LAST_NAME, 
                AGE,BANK_ACCOUNT,GENDER, EMAIL,
                HOUSE_NO,STREET,POSTAL_CODE,CITY
                FROM CUSTOMER WHERE CUSTOMER_ID = '""" + id + "';"
    cursor.execute(sql)
    table = cursor.fetchall()

    for data in table:
        id = data[0]
        first_name = data[1]
        last_name = data[2]
        age = data[3]
        bank = data[4]
        gender = data[5]
        email = data[6]
        house = data[7]
        street = data[8]
        postal_code = data[9]
        city = data[10]
        row = {'first_name': first_name, 'last_name': last_name, 'age': age, 'bank': bank, 'gender': gender,
               'email': email, 'house': house, 'street': street, 'postal_code': postal_code, 'city': city}
        dictionary.append(row)

    id = str(id)
    cursor = connection.cursor()
    sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE CUSTOMER_ID = '" + id + "';"
    cursor.execute(sql)
    numbers = cursor.fetchall()
    total_numbers = len(numbers)

    phone1 = 0
    phone2 = 0
    phone3 = 0

    if total_numbers == 1:
        phone1 = int(numbers[0][0])
    if total_numbers == 2:
        phone1 = int(numbers[0][0])
        phone2 = int(numbers[1][0])
    if total_numbers == 3:
        phone1 = int(numbers[0][0])
        phone2 = int(numbers[1][0])
        phone3 = int(numbers[2][0])

    row = {'phone1': phone1, 'phone2': phone2, 'phone3': phone3}
    phone_dict.append(row)

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

    sql = "SELECT EMAIL FROM CUSTOMER WHERE CUSTOMER_ID = " + id
    cursor.execute(sql)
    name_table = cursor.fetchall()
    username = [data[0] for data in name_table]
    username = str(username[0])

    cursor.close()


def load_profile(request):
    global id
    global dictionary
    global phone_dict
    global category_dict
    global username
    global phone1
    global phone2
    global phone3
    global msg

    # send to login if no session exists:
    if not ('customer_id' in request.session):
        return redirect(login_views.load_login)

    msg = ""
    keep_running_profile(request)

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

    # EDITING PROFILE ~
    if request.method == 'POST':
        id = str(id)
        if 'bank' in request.POST:
            bank = request.POST['bank']
            if len(bank) != 0:
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET BANK_ACCOUNT = '" + bank + "' WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                cursor.close()

        if 'house' in request.POST:
            house = request.POST['house']
            if len(house) != 0:
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET HOUSE_NO = '" + house + "' WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                cursor.close()

        if 'street' in request.POST:
            street = request.POST['street']
            if len(street) != 0:
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET STREET = '" + street + "' WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                cursor.close()

        if 'postal_code' in request.POST:
            postal_code = request.POST['postal_code']
            if len(postal_code) != 0:
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET POSTAL_CODE = '" + postal_code + "' WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                cursor.close()

        if 'city' in request.POST:
            city = request.POST['city']
            if len(city) != 0:
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET CITY = '" + city + "' WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                cursor.close()

        if 'email' in request.POST:
            email = request.POST['email']
            if len(email) != 0:
                cursor = connection.cursor()
                sql = "SELECT EMAIL FROM CUSTOMER WHERE EMAIL = '" + email + "';"
                cursor.execute(sql)
                emails_ = cursor.fetchall()
                email_fetched = ""
                if cursor.rowcount > 0:
                    email_fetched = [x[0] for x in emails_]
                    email_fetched = str(email_fetched[0])
                # email already in use given!
                if email_fetched == email:
                    msg = "Email Already in Use"
                    return render(request, 'myProfile.html', {'dictionary': dictionary, 'username': username,
                                                              'err': msg, 'items_len': cart_item_no,
                                                              'phone_number': phone_dict, 'categories': category_dict})
                else:
                    cursor = connection.cursor()
                    sql = "UPDATE CUSTOMER SET EMAIL = '" + email + "' WHERE CUSTOMER_ID = '" + id + "';"
                    cursor.execute(sql)
                    cursor.close()

        if 'old_password' in request.POST:
            old_password = request.POST['old_password']
            if len(old_password) != 0:
                old_password = hashlib.md5(old_password.encode('utf-8')).hexdigest()
                cursor = connection.cursor()
                sql = "SELECT PASSWORD FROM CUSTOMER WHERE CUSTOMER_ID = '" + id + "';"
                cursor.execute(sql)
                passwords_ = cursor.fetchall()
                password_fetched = ""
                if cursor.rowcount > 0:
                    password_fetched = [x[0] for x in passwords_]
                    password_fetched = str(password_fetched[0])
                if password_fetched == old_password:
                    if 'password' in request.POST:
                        password = request.POST['password']
                        if len(password) != 0:
                            password = hashlib.md5(password.encode('utf-8')).hexdigest()
                            cursor = connection.cursor()
                            sql = "UPDATE CUSTOMER SET PASSWORD = '" + password + "' WHERE CUSTOMER_ID = '" + id + "';"
                            cursor.execute(sql)
                            cursor.close()
                        else:
                            # new password empty
                            msg = "New Password Not Given!"
                            return render(request, 'myProfile.html', {'dictionary': dictionary,
                                                                      'username': username, 'err': msg,
                                                                      'phone_number': phone_dict,
                                                                      'categories': category_dict,
                                                                      'items_len': cart_item_no})
                else:
                    # old password does not match
                    msg = "Current Password Incorrect"
                    return render(request, 'myProfile.html',
                                  {'dictionary': dictionary, 'username': username, 'err': msg,
                                   'phone_number': phone_dict, 'categories': category_dict,
                                   'items_len': cart_item_no})

        if 'phone' in request.POST:
            phone = request.POST['phone']
            phone = convert_number(phone)
            if len(phone) != 0:
                cursor = connection.cursor()
                sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone + "';"
                cursor.execute(sql)
                number1 = cursor.fetchall()
                number_fetched = -1
                if cursor.rowcount > 0:
                    number_fetched = [x[0] for x in number1]
                    number_fetched = str(number_fetched[0])

                if number_fetched == phone:
                    msg = "Phone Number Already in Use"
                    return render(request, 'myProfile.html',
                                  {'dictionary': dictionary, 'username': username, 'err': msg,
                                   'phone_number': phone_dict, 'categories': category_dict,
                                   'items_len': cart_item_no})
                else:
                    phone1 = str(phone1)
                    cursor = connection.cursor()
                    sql = "DELETE FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone1 + "';"
                    cursor.execute(sql)

                    phone = str(phone)
                    cursor = connection.cursor()
                    sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone + ", " + id + ");"
                    cursor.execute(sql)
                    cursor.close()

        if 'phone_2' in request.POST:
            phone_2 = request.POST['phone_2']
            phone_2 = convert_number(phone_2)
            if len(phone_2) != 0:
                cursor = connection.cursor()
                sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone_2 + "';"
                cursor.execute(sql)
                number1 = cursor.fetchall()
                number_fetched = -1
                if cursor.rowcount > 0:
                    number_fetched = [x[0] for x in number1]
                    number_fetched = str(number_fetched[0])

                if number_fetched == phone_2:
                    msg = "Phone Number 2 Already in Use"
                    return render(request, 'myProfile.html',
                                  {'dictionary': dictionary, 'username': username, 'err': msg,
                                   'phone_number': phone_dict, 'categories': category_dict,
                                   'items_len': cart_item_no})
                else:
                    phone2 = str(phone2)
                    cursor = connection.cursor()
                    sql = "DELETE FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone2 + "';"
                    cursor.execute(sql)

                    phone_2 = str(phone_2)
                    cursor = connection.cursor()
                    sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone_2 + ", " + id + ");"
                    cursor.execute(sql)
                    cursor.close()

        if 'phone_3' in request.POST:
            phone_3 = request.POST['phone_3']
            phone_3 = convert_number(phone_3)
            if len(phone_3) != 0:
                cursor = connection.cursor()
                sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone_3 + "';"
                cursor.execute(sql)
                number1 = cursor.fetchall()
                number_fetched = -1
                if cursor.rowcount > 0:
                    number_fetched = [x[0] for x in number1]
                    number_fetched = str(number_fetched[0])

                if number_fetched == phone_3:
                    msg = "Phone Number 3 Already in Use"
                    return render(request, 'myProfile.html',
                                  {'dictionary': dictionary, 'username': username, 'err': msg,
                                   'phone_number': phone_dict, 'categories': category_dict,
                                   'items_len': cart_item_no})
                else:
                    phone3 = str(phone3)
                    cursor = connection.cursor()
                    sql = "DELETE FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone3 + "';"
                    cursor.execute(sql)

                    phone_3 = str(phone_3)
                    cursor = connection.cursor()
                    sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone_3 + ", " + id + ");"
                    cursor.execute(sql)
                    cursor.close()

        keep_running_profile(request)  # reloads profile after changes made
        return render(request, 'myProfile.html', {'dictionary': dictionary, 'username': username, 'err': msg,
                                                  'phone_number': phone_dict, 'categories': category_dict,
                                                  'items_len': cart_item_no})
    else:
        return render(request, 'myProfile.html', {'dictionary': dictionary, 'username': username, 'err': msg,
                                                  'phone_number': phone_dict, 'categories': category_dict,
                                                  'items_len': cart_item_no})




