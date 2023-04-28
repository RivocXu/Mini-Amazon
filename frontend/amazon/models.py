from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User

class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    email = models.EmailField(max_length=64)
    password = models.CharField(max_length=64)
    location_x = models.IntegerField()
    location_y = models.IntegerField()

    def __str__(self):
        return self.name
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)     # item_id
    description = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    products = models.ManyToManyField(Product, through='CartItem', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_created)

    def add_product(self, product, quantity):
        item, created = CartItem.objects.get_or_create(cart=self, product=product)
        item.quantity += quantity
        item.save()

    def remove_product(self, product, quantity):
        try:
            item = CartItem.objects.get(cart=self, product=product)
        except CartItem.DoesNotExist:
            return
        if item.quantity > quantity:
            item.quantity -= quantity
            item.save()
        else:
            item.delete()

    def clear(self):
        self.products.clear()

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cartitem_set.all())

    def get_product_count(self):
        return sum(item.quantity for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity

class placeOrder(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=64)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    items = models.ManyToManyField(Product, through='placeOrderItem', blank=True)
    # time = models.DateTimeField(auto_now_add=True)
    # STATUS_CHOICES = [
    #     ('PACKING', 'packing'),
    #     ('PACKED', 'packed'),
    #     ('LOADING', 'loading'),
    #     ('LOADED', 'loaded'),
    #     ('DELIVERING', 'delivering'),
    #     ('DELIVERED', 'delivered'),
    # ]
    # status = models.CharField(
    #     max_length=64, choices=STATUS_CHOICES, default='packing')
    
    def add_item(self, product, count):
        item, created = placeOrderItem.objects.get_or_create(order=self, product=product, count=count)

class placeOrderItem(models.Model):
    order = models.ForeignKey(placeOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} x {self.count}"
    
class Orders(models.Model):
    class OrderStatus(models.TextChoices):
        CART = 'cart'
        PACKING = 'packing'
        PACKED = 'packed'
        LOADING = 'loading'
        LOADED = 'loaded'
        DELIVERING = 'delivering'
        DELIVERED = 'delivered'
        
    user_name = models.CharField(max_length=64)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    wh_id = models.IntegerField(null=True)
    wh_location_x = models.IntegerField(null=True)
    wh_location_y = models.IntegerField(null=True)
    truck_id = models.IntegerField(null=True)
    status = models.CharField(choices=OrderStatus.choices, max_length=20)
    note = models.TextField(null=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Orders, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE)
    count = models.IntegerField()
    
# class Warehouse(models.Model):
#     location_x = models.IntegerField()
#     location_y = models.IntegerField()







