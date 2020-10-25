from django.shortcuts import render
from django.db import connection


# Create your views here.
def load_home(request):

    cursor = connection.cursor()
    sql = "SELECT * FROM CATEGORY_NAME"
    cursor.execute(sql)
    categories = cursor.fetchall()


    category_dict = []

    for r in categories:
        category = r[0]
        row = {'category': category}
        category_dict.append(row)


    sql = "SELECT NAME, BRAND, PRICE, IMAGE_LINK FROM PRODUCT"
    cursor.execute(sql)
    product_list = cursor.fetchall()
    cursor.close()

    product_dict = []

    for r in product_list:
        name = r[0]
        brand = r[1]
        price = r[2]
        image_link = r[3]
        row = {'name': name, 'brand':brand, 'price': price, 'image_link':image_link}
        product_dict.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'home.html', {'categories': category_dict, 'products': product_dict})
