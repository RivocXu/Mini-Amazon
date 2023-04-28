from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UserInfo, placeOrder, Product, Cart, Orders
from .forms import RegistrationForm, placeOrderForm, LoginForm
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .client import sendMsg

def register(request):
    if request.method == 'POST':
        # print('111')
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # print('222')
            form.save()
            # 注册成功后自动登录
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        #print('333')
        form = RegistrationForm()
    return render(request, 'amazon/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # print("success!")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'amazon/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    user1 = UserInfo.objects.filter(name = request.user.username)
    # 需要处理没有object的情况吗？
    return render(request, 'amazon/home.html', {})

@login_required
def placeANewOrder(request):
    current_user = request.user
    if request.method == 'POST':
        form = placeOrderForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data['user_name']
            location_x = form.cleaned_data['location_x']
            location_y = form.cleaned_data['location_y']
            
            newOrder = placeOrder.objects.create(user_name=user_name, location_x=location_x, location_y=location_y)
            
            # cart = Cart.objects.first()
            cart = Cart.objects.get_or_create(user=current_user)[0]
            items = cart.cartitem_set.all()
            for item in items:
                newOrder.add_item(item.product, item.quantity)
            
            cart.clear()    # Clear the cart
            
            newOrder.save()
            sendMsg(str(newOrder.id))
            return redirect('orderSuccess')
    else:
        form = placeOrderForm()
    return render(request, 'amazon/placeOrder.html', {'form': form})

@login_required
def orderSuccess(request):
    return render(request, 'amazon/orderSuccess.html')

@login_required
def productList(request):
    products = Product.objects.all()
    # cart = Cart.objects.first()  # Create a new cart
    current_user = request.user
    cart = Cart.objects.get_or_create(user=current_user)[0]

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = Product.objects.get(id=product_id)
        cart.add_product(product, quantity)

        return redirect('productList')

    context = {
        'products': products,
        'cart': cart,
    }
    
    return render(request, 'amazon/productList.html', context)

@login_required
def viewCart(request):
    # cart = Cart.objects.first()
    current_user = request.user
    cart = Cart.objects.get_or_create(user=current_user)[0]
    items = cart.cartitem_set.all()
    total_price = cart.get_total_price()
    context = {
        'items': items,
        'total_price': total_price
    }
    return render(request, 'amazon/viewCart.html', context)

@login_required
def orderList(request):
    # print(request.user.username)
    orderlist = Orders.objects.filter(user_name__iexact=request.user.username)
    # for order in orderlist:
    #     sendMsg(f'check status: {order.id}')
    # orderlist = Orders.objects.all()
    # if not orderlist:
    #     print("No result")
    # else:
    #     for order in orderlist:
    #         print(order.id)
    context = {'orders': orderlist}
    return render(request, 'amazon/orderList.html', context)

@login_required
def orderDetail(request, order_id):
    # sendMsg(f'check status: {order_id}')
    order = Orders.objects.filter(id=order_id, user_name=request.user.username).first()
    if order.status != 'packing':
        sendMsg(f'check status: {order_id}')
    items = order.order_items.all()
    status = order.status
    if not order:
        # return 404 page or redirect to order list page
        pass
    context = {'order': order, 'items': items, 'status': status}
    return render(request, 'amazon/orderDetail.html', context)

# def checkOrderStatus(request):
#     list = 
#     return render(request, 'amazon/orderStsatus.html')