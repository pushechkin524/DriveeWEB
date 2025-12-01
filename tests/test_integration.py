import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from decimal import Decimal

from accounts.models import Role, User
from store.models import (
    Brand,
    Category,
    Product,
    Cart,
    CartItem,
    PickupPoint,
)


def auth_client(user: User) -> APIClient:
    """Возвращает APIClient с заголовком Authorization для пользователя."""
    # SimpleJWT по умолчанию ожидает поле id; у нас ключ user_id.
    api_settings.USER_ID_FIELD = "user_id"
    api_settings.USER_ID_CLAIM = "user_id"
    # Добавим алиас id, чтобы for_user не падал
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
        email="admin@example.com",
        password="pass1234",
        role=role_admin,
        is_staff=True,
    )


@pytest.fixture
def regular_user(db, role_user):
    return User.objects.create_user(
        email="user@example.com",
        password="pass1234",
        role=role_user,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name="Filters")


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Bosch")


@pytest.fixture
def product(db, category, brand):
    return Product.objects.create(
        name="Oil Filter",
        price="199.99",
        category=category,
        brand=brand,
    )


@pytest.mark.django_db
def test_admin_can_create_brand_regular_gets_403(admin_user, regular_user):
    # Админ создаёт бренд успешно
    admin_client = auth_client(admin_user)
    resp = admin_client.post("/api/store/brands/", {"name": "NewBrand"})
    assert resp.status_code == 201

    # Обычный пользователь не может создавать бренды
    user_client = auth_client(regular_user)
    resp_forbidden = user_client.post("/api/store/brands/", {"name": "FailBrand"})
    assert resp_forbidden.status_code == 403


@pytest.mark.django_db
def test_cart_to_order_request_flow(admin_user, regular_user, product):
    client = auth_client(regular_user)
    admin_client = auth_client(admin_user)

    resp_cart = client.post("/api/store/carts/", {"user": regular_user.pk})
    assert resp_cart.status_code == 201
    cart_id = resp_cart.data["id"]

    resp_item = client.post(
        "/api/store/cart-items/",
        {"cart": cart_id, "product": product.pk, "quantity": 2},
    )
    assert resp_item.status_code == 201

    resp_pickup = admin_client.post(
        "/api/store/pickup-points/",
        {
            "name": "Main PVZ",
            "company": "Drivee",
            "address": "Test street, 1",
            "working_hours": "10-20",
            "is_active": True,
        },
    )
    assert resp_pickup.status_code == 201
    pickup_id = resp_pickup.data["id"]

    price_val = Decimal(product.price)
    cart_snapshot = [
        {"product_id": product.pk, "name": product.name, "quantity": 2, "price": float(price_val)}
    ]
    total_amount = float(price_val * 2)
    resp_order = client.post(
        "/api/store/order-requests/",
        {
            "user": regular_user.pk,
            "full_name": "Test User",
            "phone": "+100000000",
            "email": "user@example.com",
            "delivery_type": "pickup",
            "pickup_point": pickup_id,
            "payment_method": "card_now",
            "cart_snapshot": cart_snapshot,
            "total_amount": total_amount,
            "status": "new",
            "accept_terms": True,
        },
        format="json",
    )
    assert resp_order.status_code == 201, resp_order.data
    assert float(resp_order.data["total_amount"]) == pytest.approx(total_amount, rel=1e-6)
    assert resp_order.data["pickup_point"] == pickup_id
    assert resp_order.data["user"] == regular_user.pk


@pytest.mark.django_db
def test_product_one_to_one_spec_unique(admin_user, category, brand):
    client = auth_client(admin_user)
    resp_product = client.post(
        "/api/store/products/",
        {
            "name": "Brake Pad",
            "price": "999.00",
            "category": category.pk,
            "brand": brand.pk,
            "product_type": "auto_part",
        },
    )
    assert resp_product.status_code == 201
    prod_id = resp_product.data["id"]

    # Первая спецификация создаётся
    resp_spec = client.post(
        "/api/store/auto-part-specs/",
        {"product": prod_id, "oem_number": "OEM123"},
    )
    assert resp_spec.status_code == 201

    # Вторая для того же товара должна дать ошибку (OneToOne)
    resp_spec_dup = client.post(
        "/api/store/auto-part-specs/",
        {"product": prod_id, "oem_number": "OEM999"},
    )
    assert resp_spec_dup.status_code in (400, 409)


@pytest.mark.django_db
def test_product_compatible_cars_m2m(admin_user, category, brand):
    client = auth_client(admin_user)
    # Создаём продукт
    resp_product = client.post(
        "/api/store/products/",
        {
            "name": "Wiper",
            "price": "199.00",
            "category": category.pk,
            "brand": brand.pk,
        },
    )
    assert resp_product.status_code == 201
    prod_id = resp_product.data["id"]

    # Создаём автомобили
    car1 = client.post("/api/store/cars/", {"make": "VW", "model": "Golf", "generation": "7"})
    car2 = client.post("/api/store/cars/", {"make": "Toyota", "model": "Corolla", "generation": "E210"})
    assert car1.status_code == 201 and car2.status_code == 201

    # Привязываем M2M (через PATCH продукта с полем compatible_cars)
    resp_patch = client.patch(
        f"/api/store/products/{prod_id}/",
        {"compatible_cars": [car1.data["id"], car2.data["id"]]},
        format="json",
    )
    assert resp_patch.status_code in (200, 202)

    # Проверяем, что связь сохранилась
    resp_get = client.get(f"/api/store/products/{prod_id}/")
    assert resp_get.status_code == 200
    assert set(resp_get.data.get("compatible_cars", [])) == {car1.data["id"], car2.data["id"]}
