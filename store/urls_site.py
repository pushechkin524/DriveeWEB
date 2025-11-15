from django.urls import path
from . import views_site as views


urlpatterns = [
    path("", views.home, name="home"),
    path("favorites/", views.favorites, name="favorites"),
    path("catalog/", views.catalog, name="catalog"),
    path("categories/", views.categories_view, name="categories"),
    path("categories/<str:main_category>/", views.category_detail_view, name="category_detail"),
    path("brands/<int:pk>/", views.brand_detail, name="brand_detail"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "cart/item/<int:item_id>/update/",
        views.update_cart_item,
        name="update_cart_item",
    ),
    path(
        "cart/item/<int:item_id>/remove/",
        views.remove_cart_item,
        name="remove_cart_item",
    ),
]
