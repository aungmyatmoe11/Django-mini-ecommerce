from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.http import JsonResponse,HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# @method_decorator(login_required, name='dispatch')

from .models import Category, Product, Customer, Cart, Order, OrderProduct
from .forms import CustomerRegistrationForm, CustomerProfileForm
import json


def home(request):
    categories = Category.objects.prefetch_related('product_set').all()
    cart_count = get_cart_count(request)
        
    context = {
        'categories': categories,
        'cart_count': cart_count,
    }
    return render(request, "app/index.html", context)


class CategoryView(View):
    def get(self, request, id):
        cart_count = get_cart_count(request)
        category = get_object_or_404(Category, id=id)
        products = Product.objects.filter(category=category)
        # products = Product.objects.filter(category=id)
        # categories = Product.objects.filter(category=category).values('name','id').annotate(total=Count('name'))
        return render(request, "app/category.html", locals())


class ProductDetail(View):
    def get(self, request, id):
        cart_count = get_cart_count(request)
        product = get_object_or_404(Product, id=id)

        return render(request, "app/productdetail.html", locals())


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "auth/register.html", locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, "Congratulation! User Register Successfully!")
            # return render(request, "auth/login.html", locals())
            return redirect("login")
        else:
            messages.warning(request, "Invalid Input Data")
            return render(request, "auth/register.html", locals())


# class PasswordChangeView(View):
#     def get(self, request,):
#         return HttpResponse('GET request!')

#     def post(self, request,):
#         return HttpResponse('POST request!')


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, "app/profile.html", locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data["name"]
            phone = form.cleaned_data["phone"]

            reg = Customer(
                user=user,
                name=name,
                phone=phone,
            )
            reg.save()
            messages.success(request, "Congratulation! Profile Save Successfully!")
        else:
            messages.warning(request, "Invalid Input Data")

        return render(request, "app/profile.html", locals())

# buynow


def show_cart(request):
    user = request.user
    cart_count = get_cart_count(request)
    carts = Cart.objects.filter(user=user)
    products_amount = 0
    shipping_fee = SHIPPING_FEE
    for p in carts:
        products_amount += int(p.product.price * p.quantity)
        p.product.price = int(p.product.price)

    total_amount = int(products_amount + SHIPPING_FEE)

    return render(request, "app/add_to_cart.html", locals())


# def plus_cart(request):
#     if request.method == "GET":
#         user = request.user
#         product_id = request.GET["product_id"]
#         c = Cart.objects.get(Q(product=product_id) & Q(user=user))
#         c.quantity += 1
#         c.save()

#         cart = Cart.objects.filter(user=user)
#         products_amount = 0
#         shipping_fee = 40
#         for p in cart:
#             products_amount += p.product.price * p.quantity

#         total_amount = products_amount + shipping_fee
#         data = {
#             "quantity": c.quantity,
#             "products_amount": products_amount,
#             "total_amount": total_amount,
#         }

#         return JsonResponse(data)


# def minus_cart(request):
#     if request.method == "GET":
#         user = request.user
#         product_id = request.GET["product_id"]
#         c = Cart.objects.get(Q(product=product_id) & Q(user=user))
#         c.quantity += 1
#         c.save()

#         cart = Cart.objects.filter(user=user)
#         products_amount = 0
#         shipping_fee = 40
#         for p in cart:
#             products_amount += p.product.price * p.quantity

#         total_amount = products_amount + shipping_fee
#         data = {
#             "quantity": c.quantity,
#             "products_amount": products_amount,
#             "total_amount": total_amount,
#         }

#         return JsonResponse(data)


PLUS = "plus"
MINUS = "minus"
REMOVE = 'remove'
SHIPPING_FEE = 40

@login_required(login_url="/accounts/login")
def add_to_cart(request):
    user = request.user
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))
    

    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = Cart.objects.get(Q(product=product) & Q(user=user))
    except Cart.DoesNotExist:
        cart_item = None

    data = {
        'user' : request.user,
        "type" : request.POST.get('type','plus'),
        "quantity" : quantity,
        "product_id" : product_id,
        "cart_item" : cart_item,
    }
    cart_action(data)

    next_url = request.GET.get('next', 'show_cart')
    return redirect(next_url)
    

# Use csrf_exempt if you're having issues with CSRF, otherwise, it's better to use CSRF protection
# @method_decorator(login_required, name='dispatch')
# @method_decorator(csrf_exempt, name='dispatch')
@csrf_exempt
@login_required
def add_to_cart_quantity(request):
    user = request.user
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        action_type = data.get('type', 'plus')

        # Ensure quantity is an integer
        quantity = int(quantity)
        product = get_object_or_404(Product, id=product_id)

        try:
            cart_item = Cart.objects.get(Q(product=product) & Q(user=user))
        except Cart.DoesNotExist:
            cart_item = None

        cart_data = {
            'user': user,
            'type': action_type,
            'quantity': quantity,
            'product_id': product_id,
            'cart_item': cart_item,
        }
        cart_action(cart_data)

        cart = Cart.objects.filter(user=user)
        products_amount = sum(item.product.price * item.quantity for item in cart)
        total_amount = products_amount + SHIPPING_FEE

        data = {
            "quantity": 0 if action_type == REMOVE else cart_item.quantity,
            "products_amount": products_amount,
            "shipping_fee": SHIPPING_FEE,
            "total_amount": total_amount,
            # "cart" : cart
        }

        return JsonResponse(data)

    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': 'Invalid data', 'details': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def cart_action(data):
    action_type = data.get('type', 'plus')
    product_id = data.get('product_id')
    cart_item = data.get('cart_item')
    quantity = data.get('quantity',1)
    user = data.get('user')

    if action_type == 'plus':
        if cart_item is None:
            cart_item = Cart.objects.create(product_id=product_id, user=user, quantity=quantity)
        else:
            cart_item.quantity += quantity
            cart_item.save()

    elif action_type == 'minus':
        if cart_item:
            cart_item.quantity -= quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()

    elif action_type == 'remove':
        if cart_item:
            cart_item.delete()

def get_cart_count(request):
    user = request.user
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        # return Cart.objects.filter(user=user).count()
        if cart_count is None:
            cart_count = 0
    else:
        cart_count = 0
    return cart_count


class CheckoutView(LoginRequiredMixin, View):
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        user = request.user
        cart_count = get_cart_count(request)
        carts = Cart.objects.filter(user=user)
        products_amount = 0
        shipping_fee = SHIPPING_FEE
        
        for p in carts:
            products_amount += int(p.product.price * p.quantity)
            p.product.price = int(p.product.price)

        total_amount = int(products_amount + SHIPPING_FEE)

        return render(request, "app/checkout.html", locals())
    
    def post(self, request, *args, **kwargs):
        user = request.user
        carts = Cart.objects.filter(user=user)

        # Check if there is enough stock for all items in the cart
        for cart in carts:
            if cart.quantity > cart.product.stock:
                return HttpResponseBadRequest(f"Not enough stock for {cart.product.name}")

        total_quantity = sum(cart.quantity for cart in carts)
        products_amount = sum(int(cart.product.price * cart.quantity) for cart in carts)
        shipping_fee = SHIPPING_FEE
        total_amount = products_amount + shipping_fee

        # Use transaction.atomic() to ensure all or none operations
        with transaction.atomic():
            # Create the Order instance
            order = Order.objects.create(
                user=user,
                total_quantity=total_quantity,
                total_amount=total_amount,
                shipping_fee=shipping_fee,
                full_name=request.POST.get('full_name'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                country=request.POST.get('country'),
                postcode=request.POST.get('postal_code'),
            )

            # Create OrderProduct instances
            order_products = [
                OrderProduct(
                    user=user,
                    order=order,
                    product=cart.product,
                    quantity=cart.quantity,
                    price=cart.product.price,
                )
                for cart in carts
            ]

            # Bulk create OrderProduct instances
            OrderProduct.objects.bulk_create(order_products)

            # Reduce stock for each product
            for cart in carts:
                product = cart.product
                product.stock -= cart.quantity
                product.save()

            # Clear the user's cart
            carts.delete()
        return redirect('index')

class OrderView(LoginRequiredMixin, View):
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        cart_count = get_cart_count(request)
        orders = Order.objects.filter(user=request.user).prefetch_related('orderproduct_set__product')

        return render(request, "app/orders.html", locals())
    # def post(self, request, *args, **kwargs):
        # return HttpResponse('POST request!')