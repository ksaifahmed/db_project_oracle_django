from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection


def load_data(request):
    cursor = connection.cursor()

    if request.method == 'POST':
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
        phone_num_1 = request.POST['phone_number_1']
        phone_num_2 = request.POST['phone_number_2']

        phone_num_1 = str(phone_num_1)
        phone_num_2 = str(phone_num_2)

        # checking whether email exists:
        sql = "SELECT PHONE_NUMBER FROM CUSTOMER_PHONE WHERE PHONE_NUMBER = " + phone_num_1 + ";"
        cursor.execute(sql)
        if cursor.rowcount == 0:
            return HttpResponse('Phone Number Already In Use')

        # new customer_id(pk) is max(id)+1
        sql = "SELECT MAX(CUSTOMER_ID) FROM CUSTOMER;"
        cursor.execute(sql)
        val = cursor.fetchall()
        max_id = 0
        for x in val:
            max_id = x[0]
        max_id +=1

        # inserting into customer table:
        new_id = str(max_id)
        age = str(age)
        postal_code = str(postal_code)
        bank = str(bank)
        sql = "INSERT INTO CUSTOMER(CUSTOMER_ID,FIRST_NAME,LAST_NAME,AGE,BANK_ACCOUNT,GENDER,EMAIL,PASSWORD,HOUSE_NO,STREET,POSTAL_CODE,CITY) VALUES(" + new_id + ", '" + first_name + "', '" + last_name + "', " + age + ", " + bank + ", '" + gender + "', '" + email + "', '" + password + "', '" + house + "', '" + street + "', " + postal_code + ", '" + city + "');"
        cursor.execute(sql)
        cursor.close()
        return render(request, 'register.html')
    else:
        return render(request, 'register.html')


