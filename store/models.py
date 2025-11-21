from decimal import Decimal
import secrets
import string

from django.db import models
from django.conf import settings
from accounts.models import User
from django.utils.html import mark_safe
from django.utils.text import slugify

class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role = models.CharField(max_length=255)

    class Meta:
        db_table = "roles"


class Category(models.Model):
    class MainCategory(models.TextChoices):
        SPARE_PARTS = ("spare_parts", "Автозапчасти")
        TIRES = ("tires", "Шины")
        RIMS = ("rims", "Диски")
        BATTERIES = ("batteries", "Аккумуляторы")
        CAR_CHEMICALS = ("car_chemicals", "Автохимия")
        ACCESSORIES = ("accessories", "Аксессуары")
        TOOLS = ("tools", "Инструменты")
        WIPERS = ("wipers", "Щётки")
        ELECTRONICS = ("electronics", "Электроника")

    main_category = models.CharField(
        max_length=32,
        choices=MainCategory.choices,
        verbose_name="Главная категория",
        default=MainCategory.SPARE_PARTS,
    )
    name = models.CharField(max_length=255, verbose_name="Подкатегория")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Описание")
    group = models.ForeignKey(
        "CategoryGroup",
        null=True,
        blank=True,
        related_name="categories",
        on_delete=models.SET_NULL,
        verbose_name="Группа",
    )

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ("main_category", "name")
        ordering = ["main_category", "name"]

    def __str__(self):
        return f"{self.get_main_category_display()} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Category.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)


class CategoryGroup(models.Model):
    main_category = models.CharField(
        max_length=32,
        choices=Category.MainCategory.choices,
        verbose_name="Главная категория",
    )
    name = models.CharField(max_length=255, verbose_name="Название группы")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Группа подкатегорий"
        verbose_name_plural = "Группы подкатегорий"
        ordering = ["main_category", "order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_main_category_display()})"


class Brand(models.Model):
    brand_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, verbose_name="Описание бренда")
    image = models.ImageField(upload_to="brands/", blank=True, null=True, verbose_name="Изображение")

    class Meta:
        db_table = "brands"

    def __str__(self):
        return self.name or f"Brand #{self.brand_id}"


class Product(models.Model):
    class ProductType(models.TextChoices):
        AUTO_PART = ("auto_part", "Автозапчасть")
        AUTO_GOODS = ("auto_goods", "Автотовар")
        TIRES = ("tires", "Шины")
        RIMS = ("rims", "Диски")
        BATTERIES = ("batteries", "Аккумуляторы")

    name = models.CharField(max_length=255, verbose_name="Название товара")
    sku = models.CharField(max_length=6, unique=True, editable=False, verbose_name="Артикул")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Бренд")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Изображение")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.AUTO_PART,
        verbose_name="Тип товара",
    )
    compatible_cars = models.ManyToManyField(
        "Car",
        blank=True,
        related_name="products",
        verbose_name="Совместимые автомобили",
    )

    def image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="80" height="80" style="object-fit:cover;border-radius:8px;">')
        return "—"
    image_preview.short_description = "Превью"

    def __str__(self):
        return f"{self.name} ({self.brand})" if self.brand else self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def _ensure_sku(self):
        if self.sku:
            return
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(20):
            candidate = "".join(secrets.choice(alphabet) for _ in range(6))
            if not Product.objects.filter(sku=candidate).exists():
                self.sku = candidate
                return
        raise ValueError("Не удалось сгенерировать уникальный артикул")

    def save(self, *args, **kwargs):
        self._ensure_sku()
        super().save(*args, **kwargs)


class AutoPartSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="auto_part_spec",
        verbose_name="Товар",
    )
    oem_number = models.CharField(max_length=255, blank=True, verbose_name="OEM / Оригинальный номер")
    manufacturer_article = models.CharField(max_length=255, blank=True, verbose_name="Артикул производителя")
    brand_name = models.CharField(max_length=255, blank=True, verbose_name="Бренд / Производитель")
    compatibility = models.CharField(max_length=255, blank=True, verbose_name="Совместимость (марка, модель, год)")
    installation_side = models.CharField(max_length=255, blank=True, verbose_name="Сторона установки")
    material = models.CharField(max_length=255, blank=True, verbose_name="Материал")
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Вес, кг")
    dimensions = models.CharField(max_length=255, blank=True, verbose_name="Габариты (Д×Ш×В)")
    country_of_origin = models.CharField(max_length=255, blank=True, verbose_name="Страна производства")
    warranty = models.CharField(max_length=255, blank=True, verbose_name="Гарантия")
    certificates = models.CharField(max_length=255, blank=True, verbose_name="Сертификаты / Стандарты")

    class Meta:
        verbose_name = "Характеристики автозапчасти"
        verbose_name_plural = "Характеристики автозапчастей"

    def __str__(self):
        return f"Характеристики {self.product.name}"


class AutoGoodsSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="auto_goods_spec",
        verbose_name="Товар",
    )
    article_code = models.CharField(max_length=255, blank=True, verbose_name="Артикул / Код")
    brand_name = models.CharField(max_length=255, blank=True, verbose_name="Бренд / Производитель")
    volume_or_weight = models.CharField(max_length=255, blank=True, verbose_name="Объём / Вес")
    size = models.CharField(max_length=255, blank=True, verbose_name="Размер (Д×Ш×В)")
    material = models.CharField(max_length=255, blank=True, verbose_name="Материал")
    color = models.CharField(max_length=255, blank=True, verbose_name="Цвет")
    compatibility = models.CharField(max_length=255, blank=True, verbose_name="Совместимость / Универсальность")
    temperature_range = models.CharField(max_length=255, blank=True, verbose_name="Температурный диапазон")
    country_of_origin = models.CharField(max_length=255, blank=True, verbose_name="Страна производства")
    warranty = models.CharField(max_length=255, blank=True, verbose_name="Гарантия")
    package_contents = models.CharField(max_length=255, blank=True, verbose_name="Комплектация")

    class Meta:
        verbose_name = "Характеристики автотовара"
        verbose_name_plural = "Характеристики автотоваров"


class TireSpecification(models.Model):
    class Season(models.TextChoices):
        SUMMER = ("summer", "Летняя")
        WINTER = ("winter", "Зимняя")
        ALL_SEASON = ("all_season", "Всесезонная")

    class StudType(models.TextChoices):
        STUDDED = ("studded", "Шипованная")
        FRICTION = ("friction", "Липучка")
        NONE = ("none", "Без шипов")

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="tire_spec",
        verbose_name="Товар",
    )
    width = models.CharField(max_length=16, blank=True, verbose_name="Ширина (мм)")
    profile = models.CharField(max_length=16, blank=True, verbose_name="Профиль (%)")
    diameter = models.CharField(max_length=16, blank=True, verbose_name="Диаметр (R)")
    load_index = models.CharField(max_length=64, blank=True, verbose_name="Индекс нагрузки")
    speed_index = models.CharField(max_length=64, blank=True, verbose_name="Индекс скорости")
    season = models.CharField(max_length=16, choices=Season.choices, default=Season.SUMMER, verbose_name="Сезон")
    stud_type = models.CharField(max_length=16, choices=StudType.choices, default=StudType.NONE, verbose_name="Шипы / липучка")
    country_of_origin = models.CharField(max_length=255, blank=True, verbose_name="Страна производства")

    class Meta:
        verbose_name = "Характеристики шины"
        verbose_name_plural = "Характеристики шин"


class RimSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="rim_spec",
        verbose_name="Товар",
    )
    diameter = models.CharField(max_length=16, blank=True, verbose_name="Диаметр (R)")
    width = models.CharField(max_length=16, blank=True, verbose_name="Ширина обода")
    pcd = models.CharField(max_length=32, blank=True, verbose_name="PCD (кол-во×диаметр)")
    center_bore = models.CharField(max_length=16, blank=True, verbose_name="Центральное отверстие")
    offset = models.CharField(max_length=16, blank=True, verbose_name="Вылет (ET)")
    material = models.CharField(max_length=64, blank=True, verbose_name="Материал")
    color = models.CharField(max_length=64, blank=True, verbose_name="Цвет")
    country_of_origin = models.CharField(max_length=255, blank=True, verbose_name="Страна производства")

    class Meta:
        verbose_name = "Характеристики диска"
        verbose_name_plural = "Характеристики дисков"

    def __str__(self):
        return f"Характеристики {self.product.name}"


class BatterySpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="battery_spec",
        verbose_name="Товар",
    )
    capacity_ah = models.CharField(max_length=32, blank=True, verbose_name="Ёмкость (А·ч)")
    cold_cranking_amps = models.CharField(max_length=32, blank=True, verbose_name="Пусковой ток (A)")
    voltage = models.CharField(max_length=16, blank=True, verbose_name="Напряжение (В)")
    polarity = models.CharField(max_length=32, blank=True, verbose_name="Полярность")
    terminal_type = models.CharField(max_length=64, blank=True, verbose_name="Тип клемм")
    length_mm = models.CharField(max_length=16, blank=True, verbose_name="Длина (мм)")
    width_mm = models.CharField(max_length=16, blank=True, verbose_name="Ширина (мм)")
    height_mm = models.CharField(max_length=16, blank=True, verbose_name="Высота (мм)")
    country_of_origin = models.CharField(max_length=255, blank=True, verbose_name="Страна производства")

    class Meta:
        verbose_name = "Характеристики аккумулятора"
        verbose_name_plural = "Характеристики аккумуляторов"

    def __str__(self):
        return f"Характеристики {self.product.name}"


class Car(models.Model):
    make = models.CharField(max_length=120, verbose_name="Марка")
    model = models.CharField(max_length=120, verbose_name="Модель")
    generation = models.CharField(max_length=120, blank=True, verbose_name="Поколение")

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["make", "model", "generation"]
        unique_together = ("make", "model", "generation")

    def __str__(self):
        parts = [self.make, self.model]
        if self.generation:
            parts.append(self.generation)
        return " ".join(parts)


class UserVehicle(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Пользователь",
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name="user_vehicles",
        verbose_name="Автомобиль",
    )
    vin = models.CharField(max_length=17, blank=True, verbose_name="VIN")
    license_plate = models.CharField(max_length=16, blank=True, verbose_name="Госномер")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        verbose_name = "Личный автомобиль"
        verbose_name_plural = "Личные автомобили"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} — {self.car}"


class Address(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    Subject = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    House = models.CharField(max_length=255)
    Flat = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "addresses"


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, db_column="address_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        db_table = "customers"


class Order(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, db_column="customer_id")
    status = models.CharField(max_length=255)
    total_amount = models.CharField(max_length=255)
    delivery_method = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "orders"


class PaymentMethod(models.Model):
    id = models.BigAutoField(primary_key=True)
    method_name = models.CharField(max_length=255)

    class Meta:
        db_table = "method_pay"


class Payment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    amount = models.CharField(max_length=255)
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, db_column="method_id")
    status = models.CharField(max_length=255)
    paid_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="order_id")

    class Meta:
        db_table = "payments"


class AddressWH(models.Model):
    address_wh_id = models.BigAutoField(primary_key=True)
    Subject = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    House = models.CharField(max_length=255)

    class Meta:
        db_table = "addresses_wh"


class Warehouse(models.Model):
    warehouse_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.ForeignKey(AddressWH, on_delete=models.SET_NULL, null=True, db_column="address_id")

    class Meta:
        db_table = "warehouses"


class Stock(models.Model):
    stocks_id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="product_id")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, db_column="warehouse_id")

    class Meta:
        db_table = "stocks"

class Favorite(models.Model):
    favorite_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        "Customer", on_delete=models.CASCADE, db_column="customer_id"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, db_column="product_id"
    )

    class Meta:
        db_table = "favorites"


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user}"

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def total_cost(self):
        return sum(
            (item.product.price * item.quantity for item in self.items.select_related("product")),
            Decimal("0.00"),
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def line_total(self):
        return self.product.price * self.quantity


class PickupPoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название ПВЗ")
    company = models.CharField(max_length=120, blank=True, verbose_name="Компания")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    working_hours = models.CharField(max_length=255, blank=True, verbose_name="Время работы")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Долгота")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"

    def __str__(self):
        return self.name


class OrderRequest(models.Model):
    DELIVERY_PICKUP = "pickup"
    DELIVERY_PVZ = "pvz"

    DELIVERIES = (
        (DELIVERY_PICKUP, "Самовывоз со склада"),
        (DELIVERY_PVZ, "Доставка в ПВЗ"),
    )

    PAYMENT_CARD_NOW = "card_now"
    PAYMENT_CARD_LATER = "card_on_delivery"

    PAYMENTS = (
        (PAYMENT_CARD_NOW, "Картой сразу"),
        (PAYMENT_CARD_LATER, "Картой при получении"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_requests",
        verbose_name="Пользователь",
    )
    full_name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=32, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    delivery_type = models.CharField(max_length=20, choices=DELIVERIES, verbose_name="Тип доставки")
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ПВЗ",
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENTS, verbose_name="Оплата")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    accept_terms = models.BooleanField(default=False, verbose_name="Согласие с условиями")
    cart_snapshot = models.JSONField(verbose_name="Состав заказа")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    status = models.CharField(max_length=50, default="new", verbose_name="Статус")

    class Meta:
        verbose_name = "Заявка на заказ"
        verbose_name_plural = "Заявки на заказ"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.pk} от {self.full_name}"


class AuditLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    essence = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    date = models.DateTimeField()
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, db_column="user_id"
    )

    class Meta:
        db_table = "audit_log"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    def __str__(self):
        return f"Профиль: {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class DailyDeal(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="daily_deals",
        verbose_name="Товар дня"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        verbose_name = "Товар дня"
        verbose_name_plural = "Товары дня"
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.product.name}"


class SparePartSection(models.Model):
    icon = models.CharField(max_length=8, verbose_name="Иконка/эмодзи", default="⚙️")
    title = models.CharField(max_length=255, verbose_name="Название блока")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Раздел автозапчастей"
        verbose_name_plural = "Разделы автозапчастей"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class SparePartItem(models.Model):
    section = models.ForeignKey(
        SparePartSection,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Раздел",
    )
    name = models.CharField(max_length=255, verbose_name="Название позиции")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Позиция раздела автозапчастей"
        verbose_name_plural = "Позиции разделов автозапчастей"
        ordering = ["section", "order", "id"]

    def __str__(self):
        return self.name
