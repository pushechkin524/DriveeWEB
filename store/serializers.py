from rest_framework import serializers
from .models import (
    Category, Brand, Product,
    Address, Customer,
    Order, PaymentMethod, Payment,
    AddressWH, Warehouse, Stock, Favorite, AuditLog,
    CategoryGroup, AutoPartSpecification, AutoGoodsSpecification, TireSpecification, RimSpecification, BatterySpecification, Car, UserVehicle,
    Cart, CartItem, PickupPoint, OrderRequest, DailyDeal, SparePartSection, SparePartItem, UserProfile
)


class CategorySerializer(serializers.ModelSerializer):
    main_category_label = serializers.CharField(source="get_main_category_display", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "main_category", "main_category_label", "slug", "description", "group"]


class CategoryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryGroup
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class AutoPartSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoPartSpecification
        fields = "__all__"


class AutoGoodsSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoGoodsSpecification
        fields = "__all__"


class TireSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TireSpecification
        fields = "__all__"


class RimSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RimSpecification
        fields = "__all__"


class BatterySpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatterySpecification
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"


class UserVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVehicle
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class AddressWHSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressWH
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"


class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoint
        fields = "__all__"


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = "__all__"


class DailyDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyDeal
        fields = "__all__"


class SparePartSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePartSection
        fields = "__all__"


class SparePartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePartItem
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
