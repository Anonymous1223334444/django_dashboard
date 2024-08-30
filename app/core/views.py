from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core import models
from userprefences.models import UserPreference 
from django.contrib import messages 
from django.core.paginator import Paginator 
import json
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.db import connection
import datetime
import csv
import xlwt

from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum 

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = models.Expense.objects.filter(    
            Q(amount__istartswith=search_str) |
            Q(date__istartswith=search_str) |
            Q(description__icontains=search_str) |
            Q(category__icontains=search_str),
        ).filter(owner=request.user)
        # print(connection.queries) 
        
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def home(request):
    categories = models.Category.objects.all()
    expenses = models.Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expenses(request):
    categories = models.Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expenses.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expenses.html', context)
        
        models.Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Expense Saved Successfully')
        return redirect('expenses')
        

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = models.Expense.objects.get(pk=id)
    categories = models.Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/adit_expense.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit_expense.html', context)
        
        models.Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense Updated Successfully')
        return redirect('expenses')
    
def expense_delete(request, id):
    expense = models.Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense Removed Successfully')
    return redirect('expenses')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_month_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = models.Expense.objects.filter(owner=request.user ,date__gte=six_month_ago, date__lte=todays_date)

    finalrep = {}

    def get_category(expense):
        return expense.category 
    
    category_list = list(set(map(get_category, expenses)))  

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount

        return amount   

    for x in expenses:
        for y in expenses: 
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Date Of Expense', 'Category'])
    expenses = models.Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.date, expense.category])

    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    colums = ['Amount', 'Description', 'Date Of Expense', 'Category']

    for col_num in range(len(colums)):
        ws.write(row_num, col_num, colums[col_num], font_style)

    font_style = xlwt.XFStyle() 
    rows = models.Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'date', 'category')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


def export_pdf(request):
    # Create the HTTP response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    
    # Set the Content-Disposition header to trigger a file download
    response['Content-Disposition'] = 'attachment; filename=Expenses_{}.pdf'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    # Generate the PDF
    expenses = models.Expense.objects.filter(owner=request.user)
    total = expenses.aggregate(Sum('amount'))['amount__sum']
    html_string = render_to_string('expenses/pdf-output.html', {
        'expenses': expenses,
        'total': total,
    })
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Write the PDF data directly to the response
    response.write(pdf)
    
    return response
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + str(datetime.datetime.now()) + '.pdf'
    
    # response['Content-Transfer-Encoding'] = 'binary'
    # expenses = models.Expense.objects.filter(owner=request.user)

    # sum = expenses.aggregate(Sum('amount'))

    # html_string = render_to_string(
    #                                 'expenses/pdf-output.html', 
    #                                 {
    #                                     'expenses': expenses,
    #                                     'total': sum['amount__sum']
    #                                 }
    #                             )
    # html = HTML(string=html_string)
    # result = html.write_pdf()

    # with tempfile.NamedTemporaryFile(delete=True) as output:
    #     output.write(result)
    #     output.flush()
    #     output = open(output.name, 'rb')
    #     response.write(output.read)
    
    # return response