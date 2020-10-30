from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator
from importlib import import_module
from django.conf import settings


# Create your views here.
def load_home(request):

    # Getting categories of products:
    cursor = connection.cursor()
    sql = "SELECT DISTINCT CATEGORY FROM PRODUCT"
    cursor.execute(sql)
    categories = cursor.fetchall()
    category_dict = []
    for r in categories:
        category = r[0]
        row = {'category': category}
        category_dict.append(row)

    # Getting products list:
    sql = "SELECT NAME, BRAND, PRICE, IMAGE_LINK, PRODUCT_ID FROM PRODUCT"
    cursor.execute(sql)
    product_list = cursor.fetchall()
    cursor.close()

    product_dict = []
    for r in product_list:
        name = r[0]
        brand = r[1]
        price = r[2]
        image_link = r[3]
        id = r[4]
        row = {'name': name, 'brand': brand, 'price': price, 'image_link': image_link, 'id': id}
        product_dict.append(row)

    # Dividing product_dict returned into 9 items per page of website
    # /?page=2 is the url of second page
    paginate = Paginator(product_dict, 9)
    page = request.GET.get('page')
    product_dict = paginate.get_page(page)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'home.html', {
        'categories': category_dict, 'products': product_dict,
    })
