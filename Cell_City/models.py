from django.conf import settings
from django.db import models
from django.utils import timezone
from .utils import generate_order_id

class Brand(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField()

    def __str__(self):
        return self.name


class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    image_url = models.URLField()
    is_available = models.BooleanField(default=True)
    battery = models.CharField(max_length=50, blank=True)
    camera = models.CharField(max_length=50, blank=True)
    processor = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    storage = models.CharField(max_length=50, blank=True)
    launch_year = models.IntegerField(default=2025)

    gaming_score = models.IntegerField(default=5)
    camera_score = models.IntegerField(default=5)
    battery_score = models.IntegerField(default=5)

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}: {self.value}'
    
    def decrease_stock_quantity(self, quantity):
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.user.username


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product')

    def __str__(self):
        return f"Wishlist for {self.user.username}"

class Address(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.country}"


from .utils import generate_order_id
from django.utils import timezone



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    order_id = models.CharField(max_length=20, unique=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_cancelled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = generate_order_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_id} - {self.user.username}"

    def cancel_order(self):
        if not self.is_cancelled:
            self.is_cancelled = True
            self.save()
            order_items = OrderItem.objects.filter(order=self)
            for order_item in order_items:
                order_item.product.stock_quantity += order_item.quantity
                order_item.product.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.name

