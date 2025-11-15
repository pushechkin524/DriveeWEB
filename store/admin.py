from django.contrib import admin
from .models import (
    Category,
    Product,
    Brand,
    DailyDeal,
    Cart,
    CartItem,
    PickupPoint,
    OrderRequest,
    SparePartSection,
    SparePartItem,
    CategoryGroup,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "main_category", "group")
    list_filter = ("main_category", "group")
    search_fields = ("name",)
    autocomplete_fields = ("group",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "image_preview")
    list_filter = ("category", "brand")
    search_fields = ("name", "brand__name")
    readonly_fields = ("image_preview",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(DailyDeal)
class DailyDealAdmin(admin.ModelAdmin):
    list_display = ("product", "added_at")
    search_fields = ("product__name",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "added_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "item_count")
    search_fields = ("user__email", "user__full_name")
    inlines = (CartItemInline,)

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Позиции"


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "address")


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "delivery_type", "payment_method", "total_amount", "created_at", "status")
    list_filter = ("delivery_type", "payment_method", "status")
    search_fields = ("full_name", "email", "phone")


class SparePartItemInline(admin.TabularInline):
    model = SparePartItem
    extra = 1


@admin.register(SparePartSection)
class SparePartSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)
    search_fields = ("title", "description")
    inlines = (SparePartItemInline,)


@admin.register(CategoryGroup)
class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "main_category", "order")
    list_filter = ("main_category",)
    search_fields = ("name", "description")
    ordering = ("main_category", "order")
