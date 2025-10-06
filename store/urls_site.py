from django.urls import path
from .views_site import home, catalog, favorites

urlpatterns = [
    path("", home, name="home"),
    path("catalog/", catalog, name="catalog"),
    path("favorites/", favorites, name="favorites"),  
]
