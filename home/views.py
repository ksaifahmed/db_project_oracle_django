from django.shortcuts import render
from django.db import connection


# Create your views here.
def list_jobs(request):
    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS"
    # cursor.execute(sql)
    # result = cursor.fetchall()

    cursor = connection.cursor()
    #sql = "SELECT * FROM JOBS WHERE MIN_SALARY>%s"
    #cursor.execute(sql, [5000])
    cursor.execute("SELECT * FROM PHONE_NUMBER")
    result = cursor.fetchall()
    cursor.close()

    dict_result = []

    for r in result:
        phone_id = r[0]
        phone_no = r[1]
        row = {'phone_id': phone_id, 'phone_no': phone_no}
        dict_result.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request, 'home.html', {'phone_numbers': dict_result})
