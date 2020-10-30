from django.shortcuts import render, redirect
from django.db import connection
import home.views as homeview


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


# Create your views here.
def load_login(request):
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
