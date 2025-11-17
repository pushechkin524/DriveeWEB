from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'stocks', StockViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'audit-log', AuditLogViewSet)
router.register(r'category-groups', CategoryGroupViewSet)
router.register(r'auto-part-specs', AutoPartSpecificationViewSet)
router.register(r'auto-goods-specs', AutoGoodsSpecificationViewSet)
router.register(r'tire-specs', TireSpecificationViewSet)
router.register(r'rim-specs', RimSpecificationViewSet)
router.register(r'battery-specs', BatterySpecificationViewSet)
router.register(r'cars', CarViewSet)
router.register(r'user-vehicles', UserVehicleViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'pickup-points', PickupPointViewSet)
router.register(r'order-requests', OrderRequestViewSet)
router.register(r'daily-deals', DailyDealViewSet)
router.register(r'sparepart-sections', SparePartSectionViewSet)
router.register(r'sparepart-items', SparePartItemViewSet)
router.register(r'user-profiles', UserProfileViewSet)


urlpatterns = [path('', include(router.urls))]
