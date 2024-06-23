import random
import string
import uuid

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category', null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='product', null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


    @property
    def total_cost(self):
# (self.product.discount_price > 0 ? self.product.discount_price : self.product.price)
        return self.quantity * self.product.discount_price
    

# class Payment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
#     razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     paid = models.BooleanField(default=False)


class Order(models.Model):
    STATUS = (  # ? TUPLES like Enums
        ('pending', 'PENDING'),
        ('process', 'PROCESS'),
        ('complete', 'COMPLETE'),
        ('reject', 'REJECT'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=30, default='pending')
    total_quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tracking_code = models.CharField(max_length=10, unique=True, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    full_name = models.CharField(max_length=50,null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=50,null=True)
    country = models.CharField(max_length=50,null=True)
    postcode = models.IntegerField(null=True)

    def __str__(self):
        return f"Order {self.id}"

    def save(self, *arg, **kwargs):
        if not self.tracking_code:
            letters = string.ascii_uppercase
            numbers = ''.join(random.choices(string.digits, k=8))
            self.tracking_code = ''.join(random.choices(letters, k=2)) + numbers
            # self.tracking_code = str(uuid.uuid4()).upper()[:10]  # generate a unique tracking code
        super().save(*arg, **kwargs)

    @property
    def order_products(self):
        return self.orderproduct_set.all()

    @classmethod
    def get_order_by_tracking_code(cls, tracking_code):
        try:
            return cls.objects.get(tracking_code=tracking_code)
        except cls.DoesNotExist:
            return None


class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        # return f"{self.quantity} of {self.product.name} in order {self.order.id} [{self.order.tracking_code}]"
        return f"{self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
