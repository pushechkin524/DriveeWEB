"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib.auth import views as auth_views



urlpatterns = [
    path("", include("store.urls_site")),

    path("admin/", admin.site.urls),
    path("", include("store.urls_site")),

    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),


    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    path("api/auth/", include("accounts.urls")),
    path("api/store/", include("store.urls")),

]
