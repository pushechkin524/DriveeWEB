from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import *               
from .serializers import *          



class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


@extend_schema_view(
    list=extend_schema(tags=["Category"]),
    retrieve=extend_schema(tags=["Category"]),
    create=extend_schema(tags=["Category"]),
    update=extend_schema(tags=["Category"]),
    partial_update=extend_schema(tags=["Category"]),
    destroy=extend_schema(tags=["Category"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Brand"]),
    retrieve=extend_schema(tags=["Brand"]),
    create=extend_schema(tags=["Brand"]),
    update=extend_schema(tags=["Brand"]),
    partial_update=extend_schema(tags=["Brand"]),
    destroy=extend_schema(tags=["Brand"]),
)
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema_view(
    list=extend_schema(tags=["CategoryGroup"]),
    retrieve=extend_schema(tags=["CategoryGroup"]),
    create=extend_schema(tags=["CategoryGroup"]),
    update=extend_schema(tags=["CategoryGroup"]),
    partial_update=extend_schema(tags=["CategoryGroup"]),
    destroy=extend_schema(tags=["CategoryGroup"]),
)
class CategoryGroupViewSet(viewsets.ModelViewSet):
    queryset = CategoryGroup.objects.all()
    serializer_class = CategoryGroupSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Product"]),
    retrieve=extend_schema(tags=["Product"]),
    create=extend_schema(tags=["Product"]),
    update=extend_schema(tags=["Product"]),
    partial_update=extend_schema(tags=["Product"]),
    destroy=extend_schema(tags=["Product"]),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("brand", "category")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["brand", "category"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]

@extend_schema_view(
    list=extend_schema(tags=["Favorite"]),
    retrieve=extend_schema(tags=["Favorite"]),
    create=extend_schema(tags=["Favorite"]),
    update=extend_schema(tags=["Favorite"]),
    partial_update=extend_schema(tags=["Favorite"]),
    destroy=extend_schema(tags=["Favorite"]),
)
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.select_related("customer", "product")
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["AuditLog"]),
    retrieve=extend_schema(tags=["AuditLog"]),
    create=extend_schema(tags=["AuditLog"]),
    update=extend_schema(tags=["AuditLog"]),
    partial_update=extend_schema(tags=["AuditLog"]),
    destroy=extend_schema(tags=["AuditLog"]),
)
class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema_view(
    list=extend_schema(tags=["Customer"]),
    retrieve=extend_schema(tags=["Customer"]),
    create=extend_schema(tags=["Customer"]),
    update=extend_schema(tags=["Customer"]),
    partial_update=extend_schema(tags=["Customer"]),
    destroy=extend_schema(tags=["Customer"]),
)
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related("user", "address")
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Order"]),
    retrieve=extend_schema(tags=["Order"]),
    create=extend_schema(tags=["Order"]),
    update=extend_schema(tags=["Order"]),
    partial_update=extend_schema(tags=["Order"]),
    destroy=extend_schema(tags=["Order"]),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("customer")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Payment"]),
    retrieve=extend_schema(tags=["Payment"]),
    create=extend_schema(tags=["Payment"]),
    update=extend_schema(tags=["Payment"]),
    partial_update=extend_schema(tags=["Payment"]),
    destroy=extend_schema(tags=["Payment"]),
)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("order", "method")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["PaymentMethod"]),
    retrieve=extend_schema(tags=["PaymentMethod"]),
    create=extend_schema(tags=["PaymentMethod"]),
    update=extend_schema(tags=["PaymentMethod"]),
    partial_update=extend_schema(tags=["PaymentMethod"]),
    destroy=extend_schema(tags=["PaymentMethod"]),
)
class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Warehouse"]),
    retrieve=extend_schema(tags=["Warehouse"]),
    create=extend_schema(tags=["Warehouse"]),
    update=extend_schema(tags=["Warehouse"]),
    partial_update=extend_schema(tags=["Warehouse"]),
    destroy=extend_schema(tags=["Warehouse"]),
)
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Stock"]),
    retrieve=extend_schema(tags=["Stock"]),
    create=extend_schema(tags=["Stock"]),
    update=extend_schema(tags=["Stock"]),
    partial_update=extend_schema(tags=["Stock"]),
    destroy=extend_schema(tags=["Stock"]),
)
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related("warehouse", "product")
    serializer_class = StockSerializer
    permission_classes = [IsAdminOrReadOnly]

# New ViewSets
@extend_schema_view(
    list=extend_schema(tags=["Address"]),
    retrieve=extend_schema(tags=["Address"]),
    create=extend_schema(tags=["Address"]),
    update=extend_schema(tags=["Address"]),
    partial_update=extend_schema(tags=["Address"]),
    destroy=extend_schema(tags=["Address"]),
)
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Cart"]),
    retrieve=extend_schema(tags=["Cart"]),
    create=extend_schema(tags=["Cart"]),
    update=extend_schema(tags=["Cart"]),
    partial_update=extend_schema(tags=["Cart"]),
    destroy=extend_schema(tags=["Cart"]),
)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.select_related("user")
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["CartItem"]),
    retrieve=extend_schema(tags=["CartItem"]),
    create=extend_schema(tags=["CartItem"]),
    update=extend_schema(tags=["CartItem"]),
    partial_update=extend_schema(tags=["CartItem"]),
    destroy=extend_schema(tags=["CartItem"]),
)
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.select_related("cart", "product")
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["PickupPoint"]),
    retrieve=extend_schema(tags=["PickupPoint"]),
    create=extend_schema(tags=["PickupPoint"]),
    update=extend_schema(tags=["PickupPoint"]),
    partial_update=extend_schema(tags=["PickupPoint"]),
    destroy=extend_schema(tags=["PickupPoint"]),
)
class PickupPointViewSet(viewsets.ModelViewSet):
    queryset = PickupPoint.objects.all()
    serializer_class = PickupPointSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["OrderRequest"]),
    retrieve=extend_schema(tags=["OrderRequest"]),
    create=extend_schema(tags=["OrderRequest"]),
    update=extend_schema(tags=["OrderRequest"]),
    partial_update=extend_schema(tags=["OrderRequest"]),
    destroy=extend_schema(tags=["OrderRequest"]),
)
class OrderRequestViewSet(viewsets.ModelViewSet):
    queryset = OrderRequest.objects.select_related("user", "pickup_point")
    serializer_class = OrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["DailyDeal"]),
    retrieve=extend_schema(tags=["DailyDeal"]),
    create=extend_schema(tags=["DailyDeal"]),
    update=extend_schema(tags=["DailyDeal"]),
    partial_update=extend_schema(tags=["DailyDeal"]),
    destroy=extend_schema(tags=["DailyDeal"]),
)
class DailyDealViewSet(viewsets.ModelViewSet):
    queryset = DailyDeal.objects.select_related("product")
    serializer_class = DailyDealSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["SparePartSection"]),
    retrieve=extend_schema(tags=["SparePartSection"]),
    create=extend_schema(tags=["SparePartSection"]),
    update=extend_schema(tags=["SparePartSection"]),
    partial_update=extend_schema(tags=["SparePartSection"]),
    destroy=extend_schema(tags=["SparePartSection"]),
)
class SparePartSectionViewSet(viewsets.ModelViewSet):
    queryset = SparePartSection.objects.all()
    serializer_class = SparePartSectionSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["SparePartItem"]),
    retrieve=extend_schema(tags=["SparePartItem"]),
    create=extend_schema(tags=["SparePartItem"]),
    update=extend_schema(tags=["SparePartItem"]),
    partial_update=extend_schema(tags=["SparePartItem"]),
    destroy=extend_schema(tags=["SparePartItem"]),
)
class SparePartItemViewSet(viewsets.ModelViewSet):
    queryset = SparePartItem.objects.select_related("section")
    serializer_class = SparePartItemSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["UserProfile"]),
    retrieve=extend_schema(tags=["UserProfile"]),
    create=extend_schema(tags=["UserProfile"]),
    update=extend_schema(tags=["UserProfile"]),
    partial_update=extend_schema(tags=["UserProfile"]),
    destroy=extend_schema(tags=["UserProfile"]),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["AutoPartSpecification"]),
    retrieve=extend_schema(tags=["AutoPartSpecification"]),
    create=extend_schema(tags=["AutoPartSpecification"]),
    update=extend_schema(tags=["AutoPartSpecification"]),
    partial_update=extend_schema(tags=["AutoPartSpecification"]),
    destroy=extend_schema(tags=["AutoPartSpecification"]),
)
class AutoPartSpecificationViewSet(viewsets.ModelViewSet):
    queryset = AutoPartSpecification.objects.select_related("product")
    serializer_class = AutoPartSpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["AutoGoodsSpecification"]),
    retrieve=extend_schema(tags=["AutoGoodsSpecification"]),
    create=extend_schema(tags=["AutoGoodsSpecification"]),
    update=extend_schema(tags=["AutoGoodsSpecification"]),
    partial_update=extend_schema(tags=["AutoGoodsSpecification"]),
    destroy=extend_schema(tags=["AutoGoodsSpecification"]),
)
class AutoGoodsSpecificationViewSet(viewsets.ModelViewSet):
    queryset = AutoGoodsSpecification.objects.select_related("product")
    serializer_class = AutoGoodsSpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["TireSpecification"]),
    retrieve=extend_schema(tags=["TireSpecification"]),
    create=extend_schema(tags=["TireSpecification"]),
    update=extend_schema(tags=["TireSpecification"]),
    partial_update=extend_schema(tags=["TireSpecification"]),
    destroy=extend_schema(tags=["TireSpecification"]),
)
class TireSpecificationViewSet(viewsets.ModelViewSet):
    queryset = TireSpecification.objects.select_related("product")
    serializer_class = TireSpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["RimSpecification"]),
    retrieve=extend_schema(tags=["RimSpecification"]),
    create=extend_schema(tags=["RimSpecification"]),
    update=extend_schema(tags=["RimSpecification"]),
    partial_update=extend_schema(tags=["RimSpecification"]),
    destroy=extend_schema(tags=["RimSpecification"]),
)
class RimSpecificationViewSet(viewsets.ModelViewSet):
    queryset = RimSpecification.objects.select_related("product")
    serializer_class = RimSpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["BatterySpecification"]),
    retrieve=extend_schema(tags=["BatterySpecification"]),
    create=extend_schema(tags=["BatterySpecification"]),
    update=extend_schema(tags=["BatterySpecification"]),
    partial_update=extend_schema(tags=["BatterySpecification"]),
    destroy=extend_schema(tags=["BatterySpecification"]),
)
class BatterySpecificationViewSet(viewsets.ModelViewSet):
    queryset = BatterySpecification.objects.select_related("product")
    serializer_class = BatterySpecificationSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["Car"]),
    retrieve=extend_schema(tags=["Car"]),
    create=extend_schema(tags=["Car"]),
    update=extend_schema(tags=["Car"]),
    partial_update=extend_schema(tags=["Car"]),
    destroy=extend_schema(tags=["Car"]),
)
class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(tags=["UserVehicle"]),
    retrieve=extend_schema(tags=["UserVehicle"]),
    create=extend_schema(tags=["UserVehicle"]),
    update=extend_schema(tags=["UserVehicle"]),
    partial_update=extend_schema(tags=["UserVehicle"]),
    destroy=extend_schema(tags=["UserVehicle"]),
)
class UserVehicleViewSet(viewsets.ModelViewSet):
    queryset = UserVehicle.objects.select_related("user", "car")
    serializer_class = UserVehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
