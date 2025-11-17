from django.urls import path

from .views import admin_panel, manager_panel, orders_feed, _backup_download

app_name = "dashboard"

urlpatterns = [
    path("", admin_panel, name="admin_panel"),
    path("manager/", manager_panel, name="manager_panel"),
    path("orders-feed/", orders_feed, name="orders_feed"),
    path("backup/download/", _backup_download, name="backup_download"),
]
