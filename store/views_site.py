from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Product, Category, Brand, Favorite

def home(request):
    return render(request, "store/home.html")

def catalog(request):
    products = Product.objects.select_related("brand", "category").all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, "store/catalog.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
    })

@login_required
def favorites(request):
    favorites = Favorite.objects.select_related("product", "customer").filter(
        customer__user=request.user
    )
    return render(request, "store/favorites.html", {"favorites": favorites})

