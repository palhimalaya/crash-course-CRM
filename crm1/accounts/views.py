from tokenize import group
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate,login,logout

from .models import *
from .forms import CustomerForm, OrderForm, CreateUserForm, ProductForm

from .filters import OrderFilter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .decorators import allowed_users, unauthenticated_user, admin_only



# Create your views here.
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request, 'Username Or Password is incorrect')
            
    context = {}        
    return render(request, 'accounts/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def register(request):
   
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            
            messages.success(request, 'Account was created for '+ username)
            return redirect("login")
    
    
    context = {'form':form}
    return render(request, 'accounts/register.html',context)






@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    
    total_customers = customers.count() 
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    
    
    context = {'orders':orders,'total_customers':total_customers, 'total_orders':total_orders, 'customers':customers, 'delivered':delivered, 'pending':pending}
    
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    
    
    context = {'customer':customer, 'orders':orders, 'order_count':order_count,
               'myFilter':myFilter}
    return render(request,'accounts/customer.html',context)


    


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            product_name = form.cleaned_data.get('name')
            messages.success(request, f'{product_name} has been added')
            return redirect('products')
    else:
        form = ProductForm()
        
    context = {
        'products': products,
        'form': form,
    }
    return render(request,'accounts/products.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer','admin'])
def createOrder(request,pk):
    if group =='admin':
        OrderFormSet =  inlineformset_factory(Customer, Order, fields=('product','status'),extra=10)
    else:
        OrderFormSet =  inlineformset_factory(Customer, Order, fields=('product','note'),can_delete=False,extra=4)
    
    customer = Customer.objects.get(id=pk)
    
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm(initial={'customer':customer})
    
    
    
    if request.method == 'POST':
        # print('Printing Post:',request.POST)
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
        
    context = {'formset':formset}
    
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    
    if request.method == 'POST':
        # print('Printing Post:',request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    
    context = {'formset':form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item':order}
    return render(request, 'accounts/delete.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    
    orders = request.user.customer.order_set.all()
    id = request.user.customer.id
    
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status="Pending").count()
    
    context={'orders': orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending,'id':id}
    return render(request,'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request,pk):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_edit(request, pk):
    item = Product.objects.get(id=pk)
    form = ProductForm(instance=item)
    if request.method == 'POST':
        # print('Printing Post:',request.POST)
        form = ProductForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('products')
    
    context = {'form':form}
    return render(request, 'accounts/products_edit.html', context)
    
    
    


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('products')
    context = {
        'item': item
    }
    return render(request, 'accounts/products_delete.html', context)