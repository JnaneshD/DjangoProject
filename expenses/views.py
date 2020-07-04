from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
# Create your views here.
from django.contrib  import messages
from django.core.paginator import Paginator
import json
from userpreferences.models import UserPrefence
from django.http import JsonResponse
import datetime
def search_expenses(request):
    if request.method=="POST":
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(amount__istartswith=search_str,owner=request.user) | Expense.objects.filter(date__istartswith=search_str,owner=request.user) | Expense.objects.filter(description__icontains=search_str,owner=request.user) | Expense.objects.filter(category__icontains=search_str,owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data),safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    category = Category.objects.all()
    expense = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expense,5)
    page_number = request.GET.get('page')
    try:
        currency = UserPrefence.objects.get(user=request.user).currency
    except:
        currency = 'USD'
    page_obj = Paginator.get_page(paginator,page_number)
    context = {
        'expenses':expense,
        'page_obj':page_obj,
        'currency':currency
    }
    return render(request,'expenses/index.html',context)
def add_expenses(request):
    categories=Category.objects.all()
    context={
        'categories':categories,
        'values':request.POST
    }
    if request.method=="GET":
        return render(request,'expenses/add_expense.html',context)
    if request.method=='POST':
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense_date']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expenses/add_expense.html',context)
        if not description:
            messages.error(request,'description is required')
            return render(request,'expenses/add_expense.html',context)
        Expense.objects.create(owner=request.user,amount=amount,category=category,description=description,date=date)
        messages.success(request,'Expense saved successfully')
        return redirect('expenses')

def expense_edit(request,id):
    expense=Expense.objects.get(pk=id)
    categories=Category.objects.all()
    context = {
        'expense':expense,
        'values':expense,
        'categories':categories
    }
    if request.method=="GET":
        return render(request,'expenses/edit-expense.html',context)
    if request.method=="POST":
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense_date']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expenses/edit_expense.html',context)
        if not description:
            messages.error(request,'description is required')
            return render(request,'expenses/edit_expense.html',context)
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category= category
        expense.description = description
        expense.save()
        messages.success(request,'Expense got updated successfully')
        return redirect('expenses')
def delete_expense(request,id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense removed')
    return redirect('expenses')        

def expense_category_summary(request):
    todays_date = datetime.date.today()