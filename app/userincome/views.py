from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userincome import models
from userprefences.models import UserPreference 
from django.contrib import messages 
from django.core.paginator import Paginator 
import json
from django.http import JsonResponse
from django.db.models import Q
from django.db import connection

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes = models.UserIncome.objects.filter(    
            Q(amount__istartswith=search_str) |
            Q(date__istartswith=search_str) |
            Q(description__icontains=search_str) |
            Q(source__icontains=search_str),
        ).filter(owner=request.user)
        # print(connection.queries)
        data = incomes.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def home(request):
    source = models.Source.objects.all()
    income = models.UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = models.Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)
        
        models.UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Income Saved Successfully')
        return redirect('income')
        

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = models.UserIncome.objects.get(pk=id)
    sources = models.Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources,
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/edit_income.html', context)
        
        models.UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        income.owner = request.user
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Income Updated Successfully')
        return redirect('income')
    
def income_delete(request, id):
    income = models.UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income Removed Successfully')
    return redirect('income')