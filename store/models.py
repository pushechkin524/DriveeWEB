from django.db import models
from accounts.models import User

class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role = models.CharField(max_length=255)

    class Meta:
        db_table = "roles"


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "categories"


class Brand(models.Model):
    brand_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "brands"


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True)
    price = models.BigIntegerField()
    remainder = models.CharField(max_length=255, blank=True)
    oem_code = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, db_column="category_id")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, db_column="brand_id")

    class Meta:
        db_table = "products"


class Address(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    Subject = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    House = models.CharField(max_length=255)
    Flat = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "addresses"


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, db_column="address_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        db_table = "customers"


class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, db_column="customer_id")
    status = models.CharField(max_length=255)
    total_amount = models.CharField(max_length=255)
    delivery_method = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "orders"


class PaymentMethod(models.Model):
    id = models.BigAutoField(primary_key=True)
    method_name = models.CharField(max_length=255)

    class Meta:
        db_table = "method_pay"


class Payment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    amount = models.CharField(max_length=255)
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, db_column="method_id")
    status = models.CharField(max_length=255)
    paid_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="order_id")

    class Meta:
        db_table = "payments"


class AddressWH(models.Model):
    address_wh_id = models.BigAutoField(primary_key=True)
    Subject = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    House = models.CharField(max_length=255)

    class Meta:
        db_table = "addresses_wh"


class Warehouse(models.Model):
    warehouse_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.ForeignKey(AddressWH, on_delete=models.SET_NULL, null=True, db_column="address_id")

    class Meta:
        db_table = "warehouses"


class Stock(models.Model):
    stocks_id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="product_id")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, db_column="warehouse_id")

    class Meta:
        db_table = "stocks"

class Favorite(models.Model):
    favorite_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        "Customer", on_delete=models.CASCADE, db_column="customer_id"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, db_column="product_id"
    )

    class Meta:
        db_table = "favorites"
        
class AuditLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    essence = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    date = models.DateTimeField()
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, db_column="user_id"
    )

    class Meta:
        db_table = "audit_log"

