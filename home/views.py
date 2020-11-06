from django.shortcuts import render, redirect
from django.db import connection
from django.core.paginator import Paginator
from login.views import load_login


# Create your views here.
def load_home(request):

    # send to login if no session exists:
    if not('customer_id' in request.session):
        return redirect(load_login)

    # Getting categories of products in stock:
    cursor = connection.cursor()
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

    # Getting products list in stock:
    sql = """SELECT NAME, BRAND, PRICE, IMAGE_LINK, PRODUCT_ID, o.DESCRIPTION
            FROM THE_BAZAAR.PRODUCT p, THE_BAZAAR.OFFER o
            WHERE p.PRODUCT_ID = 
            ANY(
                SELECT PRODUCT_ID 
                FROM THE_BAZAAR.STOCK 
                WHERE EXPIRE_DATE > SYSDATE AND QUANTITY > 0
            
            UNION
            
                SELECT PRODUCT_ID
                FROM THE_BAZAAR.STOCK WHERE
                EXPIRE_DATE IS NULL AND QUANTITY > 0
            )
            
            AND p.OFFER_ID = o.OFFER_ID(+);"""

    cursor.execute(sql)
    product_list = cursor.fetchall()
    # cursor.close()

    product_dict = []
    for r in product_list:
        name = r[0]
        brand = r[1]
        price = r[2]
        image_link = r[3]
        pid = r[4]
        discount = r[5]
        row = {'name': name, 'brand': brand, 'price': price, 'image_link': image_link, 'id': pid, 'discount': discount}
        product_dict.append(row)

    customer_id = request.session.get('customer_id')
    customer_id = str(customer_id)
    sql = "SELECT EMAIL FROM CUSTOMER WHERE CUSTOMER_ID = " + customer_id
    cursor.execute(sql)
    name_table = cursor.fetchall()
    username = [data[0] for data in name_table]
    username = str(username[0])


    # Dividing product_dict returned into 9 items per page of website
    # /?page=2 is the url of second page
    paginate = Paginator(product_dict, 9)
    page = request.GET.get('page')
    product_dict = paginate.get_page(page)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'home.html', {
        'categories': category_dict, 'products': product_dict, 'username': username
    })
