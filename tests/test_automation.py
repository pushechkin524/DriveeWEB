from decimal import Decimal

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings

from accounts.models import Role, User
from store.models import (
    Brand,
    Cart,
    CartItem,
    Category,
    PickupPoint,
    Product,
)
from store.serializers import OrderRequestSerializer


def auth_client(user: User) -> APIClient:
    api_settings.USER_ID_FIELD = "user_id"
    api_settings.USER_ID_CLAIM = "user_id"
    if not hasattr(user, "id"):
        user.id = user.pk
    token = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def role_admin(db):
    role, _ = Role.objects.get_or_create(role=Role.RoleName.ADMIN)
    return role


@pytest.fixture
def role_user(db):
    role, _ = Role.objects.get_or_create(role=Role.RoleName.USER)
    return role


@pytest.fixture
def admin_user(db, role_admin):
    return User.objects.create_user(
        email="admin-auto@example.com",
        password="pass1234",
        role=role_admin,
        is_staff=True,
    )


@pytest.fixture
def regular_user(db, role_user):
    return User.objects.create_user(
        email="user-auto@example.com",
        password="pass1234",
        role=role_user,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name="AutoCat")


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="AutoBrand")


@pytest.mark.django_db
def test_product_sku_autogenerates_unique(category, brand):
    p1 = Product.objects.create(
        name="Prod1",
        price=Decimal("10.00"),
        category=category,
        brand=brand,
    )
    p2 = Product.objects.create(
        name="Prod2",
        price=Decimal("20.00"),
        category=category,
        brand=brand,
    )
    assert p1.sku and len(p1.sku) == 6
    assert p2.sku and len(p2.sku) == 6
    assert p1.sku != p2.sku


@pytest.mark.django_db
def test_cart_total_quantity_and_cost(regular_user, category, brand):
    cart = Cart.objects.create(user=regular_user)
    prod1 = Product.objects.create(name="P1", price=Decimal("5.00"), category=category, brand=brand)
    prod2 = Product.objects.create(name="P2", price=Decimal("7.50"), category=category, brand=brand)
    CartItem.objects.create(cart=cart, product=prod1, quantity=2)
    CartItem.objects.create(cart=cart, product=prod2, quantity=1)

    assert cart.total_quantity() == 3
    assert cart.total_cost() == Decimal("17.50")


@pytest.mark.django_db
def test_order_request_serializer_requires_user(category, brand):
    # Минимальный продукт и ПВЗ для валидных ссылок
    Product.objects.create(name="P3", price=Decimal("9.99"), category=category, brand=brand)
    pickup = PickupPoint.objects.create(name="PVZ", address="addr")
    data = {
        # user пропущен умышленно
        "full_name": "Test User",
        "phone": "+1000",
        "email": "a@a.a",
        "delivery_type": "pickup",
        "pickup_point": pickup.pk,
        "payment_method": "card_now",
        "cart_snapshot": [{"product_id": 1, "name": "P3", "quantity": 1, "price": 9.99}],
        "total_amount": "9.99",
        "status": "new",
        "accept_terms": True,
    }
    serializer = OrderRequestSerializer(data=data)
    assert not serializer.is_valid()
    assert "user" in serializer.errors


@pytest.mark.django_db
def test_api_controller_permissions_for_brand(admin_user, regular_user):
    admin_client = auth_client(admin_user)
    user_client = auth_client(regular_user)

    # Админ может создать бренд
    resp_admin = admin_client.post("/api/store/brands/", {"name": "AdminBrand"})
    assert resp_admin.status_code == 201

    # Пользователю запрещено создавать бренд
    resp_user = user_client.post("/api/store/brands/", {"name": "UserBrand"})
    assert resp_user.status_code == 403


@pytest.mark.django_db
def test_migrations_applied():
    # Проверяем отсутствие непримененных миграций
    call_command("migrate", check=True, plan=False, verbosity=0)
