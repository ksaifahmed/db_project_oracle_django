from django.shortcuts import render, redirect
from django.db import connection
import home.views as homeview

# sets customer id as a cookie in browser
def set_session(request, email):
    cursor = connection.cursor()
    sql = "SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL = '" + email + "';"
    cursor.execute(sql)
    table = cursor.fetchall()
    cursor.close()

    c_id = 0
    for r in table:
        c_id = r[0]
    c_id = str(c_id)

    request.session['customer_id'] = c_id


# Dummy function for testing cookies
def load_login2(request):
    # if already logged in:
    if 'customer_id' in request.session:
        return redirect(homeview.load_home)

    # if login successful, set session:
    success = True
    if success:
        email = "mehrab13@gmail.com"
        set_session(request, email)
        return redirect(homeview.load_home)

    return render(request, "login.html")


def load_login(request):
    # if already logged in:
    if 'customer_id' in request.session:
        return redirect(homeview.load_home) # sends to home view

    if request.method == 'POST':
        cursor = connection.cursor()
        email = request.POST['email']
        password = request.POST['password']

        sql = "SELECT EMAIL,PASSWORD FROM CUSTOMER WHERE EMAIL = '" + email + "';"
        cursor.execute(sql)
        email_pass = cursor.fetchall()

        email_fetched = ""
        password_fetched = ""

        # for one value, skip for loop
        if cursor.rowcount > 0: # ei line lekhtei hobe, or else error if no result in database
            # list value return kore like --> ['ridy@gmail']
            email_fetched = ([data[0] for data in email_pass])
            email_fetched = str(email_fetched[0])  # now it's just "ridy@gmail"

            password_fetched = [data[1] for data in email_pass]
            password_fetched = str(password_fetched[0])

        if email_fetched == email:
            if password_fetched == password:
                set_session(request, email)  # sets cookies for logged in users
                return redirect(homeview.load_home)  # then to home page
            return render(request, 'login.html', {'message': "Wrong Password!"})

        return render(request, 'login.html', {'message': "No such user exists"})

    else:
        return render(request, 'login.html')


# TODO : If you want user to logout, go to brower's "See all site cookies" > delete the session of "127.0.0.1"
# TODO : most of our sql in login/register returns one, value...try korsi loop baad dite
# TODO : sth like -->  phone = [row[0] for row in phone_number]
# TODO: but this returns a list, so make it string...see lines 57, 58