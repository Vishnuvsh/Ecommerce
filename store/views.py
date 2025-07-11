from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json
import datetime
from store.models import * 
from .utils import cookieCart, cartData, guestOrder
import razorpay



def main(request):
    return render(request,'store/main.html')

# SIGNIN


def signin(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('store')
        else:
            messages.info(request, " username or password is incorrect ")
            return redirect('signin')
    return render(request,'store/signin.html')


# REGISTER

def regpage(request):
    return render(request,'store/regi.html')

def regi(request):
    if request.method=='POST':
        
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST['password2']
        if Register.objects.filter(username=username).exists():
            messages.info(request,"username is already exists")
            return redirect("regi")
        
        if Register.objects.filter(email=email).exists():
            messages.info(request,"email is already exists")
            return redirect("regi")
        else:
            user=Register.objects.create_user(username=username,email=email,password=password)
            user.set_password(password)
            
            user.save()
            messages.info(request,"user successfully created")
            return redirect("signin")
    return render(request,'store/regi.html')


# STORE

def store(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
    
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)



# PAYMENT 1

def payment(request):
    return render(request,'store/payment.html')




#PAYMEMT 2
def home1(request):
    if request.method == "POST":
        name = request.POST.get('name')
        amount = 1000

        client = razorpay.Client(
            auth=("rzp_test_JAeLcxoJpwFjEq", "PvjOeaEQA5b2gH4XHxEGEhMB"))

        payment = client.order.create({'amount': amount, 'currency': 'INR',
                                       'payment_capture': '1'})
    return render(request, 'payment.html')





# CART

def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


# CHECKOUT

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)


# UPDATE ITEM

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)



# PROCESS ORDER

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)


