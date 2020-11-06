from django.shortcuts import render
from django.db import connection
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
import login.views as loginview
import hashlib
import math


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


def response_email(request):
    data = {'response': 'EMAIL already in use'}
    return JsonResponse(data)


def response_phone(request):
    data = {'response': 'Phone Number already in use'}
    return JsonResponse(data)


eligible = True


def load_data(request):
    global eligible
    eligible = True

    if request.method == 'POST':
        cursor = connection.cursor()
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        age = request.POST['age']
        bank = request.POST['bank']
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        house = request.POST['house']
        street = request.POST['street']
        postal_code = request.POST['postal_code']
        city = request.POST['city']

        phone_number = request.POST['phone_number']
        phone_number2 = request.POST['phone_number2']
        phone_number3 = request.POST['phone_number3']

        # Converting this numbers into appropriate form
        phone_number = convert_number(phone_number)
        phone_number2 = convert_number(phone_number2)
        phone_number3 = convert_number(phone_number3)

        formdata = {'first_name': first_name, 'last_name': last_name, 'age': age,
                    'bank': bank, 'gender': gender, 'email': email, 'password': password,
                    'house': house, 'street': street, 'postal_code': postal_code,
                    'city': city, 'phone_number': phone_number,
                    'phone_number2': phone_number2, 'phone_number3': phone_number3}

        # hashing the password
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # check email separately:
        # used specific sql which retrieves one email only
        sql = "SELECT EMAIL FROM CUSTOMER WHERE EMAIL = '" + email + "';"
        cursor.execute(sql)
        Emails = cursor.fetchall()
        email_fetched = ""
        if cursor.rowcount > 0:
            email_fetched = [x[0] for x in Emails]
            email_fetched = str(email_fetched[0])
        if email_fetched == email:
            eligible = False
            return render(request, 'register.html',
                          {'data': formdata, 'email_msg': 'Email Already in Use by Another Account'})

        # check phone1 separately:
        # used specific sql which retrieves one phone only
        sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone_number + "';"
        cursor.execute(sql)
        number1 = cursor.fetchall()
        number_fetched = -1
        if cursor.rowcount > 0:
            number_fetched = [x[0] for x in number1]
            number_fetched = str(number_fetched[0])

        if number_fetched == phone_number:
            eligible = False
            return render(request, 'register.html',
                          {'data': formdata, 'phone1_msg': 'Phone 1 Already in Use by Another Account'})

        # same as above phone number1:
        if phone_number2 != "":
            sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone_number2 + "';"
            cursor.execute(sql)
            number2 = cursor.fetchall()
            number_fetched = -1
            if cursor.rowcount > 0:
                number_fetched = [x[0] for x in number2]
                number_fetched = str(number_fetched[0])
            if number_fetched == phone_number2:
                eligible = False
                return render(request, 'register.html',
                              {'data': formdata, 'phone2_msg': 'Phone 2 Already in Use by Another Account'})

        # same as above phone number1:
        if phone_number3 != "":
            sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = '" + phone_number3 + "';"
            cursor.execute(sql)
            number3 = cursor.fetchall()
            number_fetched = -1
            if cursor.rowcount > 0:
                number_fetched = [x[0] for x in number3]
                number_fetched = str(number_fetched[0])
            if number_fetched == phone_number3:
                eligible = False
                return render(request, 'register.html',
                              {'data': formdata, 'phone3_msg': 'Phone 3 Already in Use by Another Account'})

        # INSERTING A NULL BANK A/C
        if bank == "":
            bank = "NULL"

        sql = "SELECT MAX(CUSTOMER_ID) FROM CUSTOMER"
        cursor.execute(sql)
        val = cursor.fetchall()
        cid = 0
        for x in val:
            cid = x[0]
        cid += 1
        cid = str(cid)
        age = str(age)
        postal_code = str(postal_code)
        bank = str(bank)

        if eligible:
            sql = "INSERT INTO CUSTOMER(CUSTOMER_ID,FIRST_NAME,LAST_NAME,AGE,BANK_ACCOUNT,GENDER,EMAIL,PASSWORD,HOUSE_NO,STREET,POSTAL_CODE,CITY) VALUES(" + cid + ", '" + first_name + "', '" + last_name + "', " + age + ", " + bank + ", '" + gender + "', '" + email + "', '" + password + "', '" + house + "', '" + street + "', " + postal_code + ", '" + city + "');"
            cursor.execute(sql)

            sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone_number + ", " + cid + ");"
            cursor.execute(sql)

            if phone_number2 != "":
                sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone_number2 + ", " + cid + ");"
                cursor.execute(sql)

            if phone_number3 != "":
                sql = "INSERT INTO CUSTOMER_PHONE(PHONE_NUMBER,CUSTOMER_ID) VALUES(" + phone_number3 + ", " + cid + ");"
                cursor.execute(sql)

            request.session['account_created'] = "Account Created Successfully"
            return redirect(loginview.load_login)  # sends to login when registered
        return render(request, 'register.html')

    else:
        return render(request, 'register.html')
