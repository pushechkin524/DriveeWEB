from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
import logging

from .forms import CheckoutForm, RegisterForm, UserVehicleForm, ProfileInfoForm
from .models import (
    Cart,
    CartItem,
    Category,
    CategoryGroup,
    DailyDeal,
    Favorite,
    PickupPoint,
    Product,
    Car,
    OrderRequest,
    Brand,
    RimSpecification,
    TireSpecification,
    Favorite,
    Customer,
    BatterySpecification,
    UserVehicle,
    UserProfile,
    AuditLog,
)


MAIN_CATEGORY_CARDS = [
    {
        "key": Category.MainCategory.SPARE_PARTS,
        "title": "Автозапчасти",
        "description": "Расходники и детали для сервиса.",
        "icon": "⚙️",
        "image": "img/аксесс.webp",
    },
    {
        "key": Category.MainCategory.TIRES,
        "title": "Шины",
        "description": "Зимние, летние и всесезонные шины.",
        "icon": "🛞",
        "image": "img/шины.png",
    },
    {
        "key": Category.MainCategory.RIMS,
        "title": "Диски",
        "description": "Литые, кованые и штампованные диски.",
        "icon": "💿",
        "image": "img/диски .jpg",
    },
    {
        "key": Category.MainCategory.BATTERIES,
        "title": "Аккумуляторы",
        "description": "Надёжный запуск в любую погоду.",
        "icon": "🔋",
        "image": "img/акум.jpg",
    },
    {
        "key": Category.MainCategory.CAR_CHEMICALS,
        "title": "Автохимия",
        "description": "Масла, жидкости и химия.",
        "icon": "🧪",
        "image": "img/химия .jpg",
    },
    {
        "key": Category.MainCategory.ACCESSORIES,
        "title": "Аксессуары",
        "description": "Комфорт и стиль для салона и кузова.",
        "icon": "🎒",
        "image": "img/аксесс.webp",
    },
    {
        "key": Category.MainCategory.TOOLS,
        "title": "Инструменты",
        "description": "Профессиональный и бытовой инструмент.",
        "icon": "🛠️",
        "image": "img/инсстру.webp",
    },
    {
        "key": Category.MainCategory.WIPERS,
        "title": "Щётки",
        "description": "Щётки стеклоочистителя для любой погоды.",
        "icon": "🧽",
        "image": "img/дворники .jpg",
    },
    {
        "key": Category.MainCategory.ELECTRONICS,
        "title": "Электроника",
        "description": "Мультимедиа и автоэлектроника.",
        "icon": "📡",
        "image": "img/электроника.jpg",
    },
]


logger = logging.getLogger(__name__)


def _audit_log(essence: str, action: str, user):
    """Safe writer for user-facing audit events."""
    try:
        AuditLog.objects.create(
            essence=essence,
            action=action,
            date=timezone.now(),
            user=user if getattr(user, "is_authenticated", False) else None,
        )
    except Exception as exc:
        logger.exception("Audit log write failed (%s / %s)", essence, action, exc_info=exc)


def home(request):
    daily_deals = DailyDeal.objects.select_related("product")[:6]
    return render(request, "store/home.html", {"daily_deals": daily_deals})


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = []
    favorites_ids = set()
    if query:
        if request.user.is_authenticated:
            favorites_ids = set(
                Favorite.objects.filter(customer__user=request.user).values_list("product_id", flat=True)
            )
        results = (
            Product.objects.select_related("brand", "category", "auto_part_spec")
            .filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(sku__icontains=query)
                | Q(auto_part_spec__oem_number__icontains=query),
                stock_quantity__gt=0,
            )
            .distinct()
        )
    return render(
        request,
        "store/search.html",
        {
            "query": query,
            "results": results,
            "favorites_ids": favorites_ids,
        },
    )


def catalog(request):
    subcategory_slug = request.GET.get("subcategory")
    main_category = request.GET.get("main_category")

    base_filters = {"stock_quantity__gt": 0}
    products_qs = Product.objects.select_related("brand", "category")
    selected_subcategory = None
    selected_main_category_label = None
    is_rims = False
    is_tires = False
    is_parts = False
    is_batteries = False
    if subcategory_slug:
        selected_subcategory = get_object_or_404(Category, slug=subcategory_slug)
        if selected_subcategory.main_category == Category.MainCategory.RIMS:
            is_rims = True
        if selected_subcategory.main_category == Category.MainCategory.TIRES:
            is_tires = True
        if selected_subcategory.main_category == Category.MainCategory.SPARE_PARTS:
            is_parts = True
        if selected_subcategory.main_category == Category.MainCategory.BATTERIES:
            is_batteries = True
        base_filters["category"] = selected_subcategory
    elif main_category:
        try:
            selected_main_category_label = Category.MainCategory(main_category).label
        except ValueError:
            raise Http404("Категория не найдена")
        if main_category == Category.MainCategory.RIMS:
            is_rims = True
        if main_category == Category.MainCategory.TIRES:
            is_tires = True
        if main_category == Category.MainCategory.SPARE_PARTS:
            is_parts = True
        if main_category == Category.MainCategory.BATTERIES:
            is_batteries = True
        base_filters["category__main_category"] = main_category

    brand_filter = ""
    diameter_filter = ""
    width_filter = ""
    pcd_filter = ""
    offset_filter = ""
    cb_filter = ""
    material_filter = ""
    color_filter = ""
    season_filter = ""
    stud_filter = ""
    profile_filter = ""
    load_index_filter = ""
    speed_index_filter = ""
    capacity_filter = ""
    cca_filter = ""
    voltage_filter = ""
    polarity_filter = ""
    terminal_filter = ""
    length_filter = ""
    height_filter = ""

    if is_rims:
        products_qs = Product.objects.select_related("brand", "category", "rim_spec").filter(
            product_type=Product.ProductType.RIMS,
            **base_filters,
        )
        brand_filter = request.GET.get("brand") or ""
        diameter_filter = request.GET.get("diameter") or ""
        width_filter = request.GET.get("width") or ""
        pcd_filter = request.GET.get("pcd") or ""
        offset_filter = request.GET.get("offset") or ""
        cb_filter = request.GET.get("center_bore") or ""
        material_filter = request.GET.get("material") or ""
        color_filter = request.GET.get("color") or ""

        if brand_filter:
            products_qs = products_qs.filter(brand_id=brand_filter)
        if diameter_filter:
            products_qs = products_qs.filter(rim_spec__diameter=diameter_filter)
        if width_filter:
            products_qs = products_qs.filter(rim_spec__width=width_filter)
        if pcd_filter:
            products_qs = products_qs.filter(rim_spec__pcd=pcd_filter)
        if offset_filter:
            products_qs = products_qs.filter(rim_spec__offset=offset_filter)
        if cb_filter:
            products_qs = products_qs.filter(rim_spec__center_bore=cb_filter)
        if material_filter:
            products_qs = products_qs.filter(rim_spec__material=material_filter)
        if color_filter:
            products_qs = products_qs.filter(rim_spec__color=color_filter)

        filter_options = {
            "brands": Brand.objects.order_by("name"),
            "diameters": RimSpecification.objects.exclude(diameter="").values_list("diameter", flat=True).distinct().order_by("diameter"),
            "widths": RimSpecification.objects.exclude(width="").values_list("width", flat=True).distinct().order_by("width"),
            "pcds": RimSpecification.objects.exclude(pcd="").values_list("pcd", flat=True).distinct().order_by("pcd"),
            "offsets": RimSpecification.objects.exclude(offset="").values_list("offset", flat=True).distinct().order_by("offset"),
            "center_bores": RimSpecification.objects.exclude(center_bore="").values_list("center_bore", flat=True).distinct().order_by("center_bore"),
            "materials": RimSpecification.objects.exclude(material="").values_list("material", flat=True).distinct().order_by("material"),
            "colors": RimSpecification.objects.exclude(color="").values_list("color", flat=True).distinct().order_by("color"),
        }
    elif is_tires:
        products_qs = Product.objects.select_related("brand", "category", "tire_spec").filter(
            product_type=Product.ProductType.TIRES,
            **base_filters,
        )
        brand_filter = request.GET.get("brand") or ""
        season_filter = request.GET.get("season") or ""
        stud_filter = request.GET.get("stud_type") or ""
        width_filter = request.GET.get("width") or ""
        profile_filter = request.GET.get("profile") or ""
        diameter_filter = request.GET.get("diameter") or ""
        load_index_filter = request.GET.get("load_index") or ""
        speed_index_filter = request.GET.get("speed_index") or ""

        if brand_filter:
            products_qs = products_qs.filter(brand_id=brand_filter)
        if season_filter:
            products_qs = products_qs.filter(tire_spec__season=season_filter)
        if stud_filter:
            products_qs = products_qs.filter(tire_spec__stud_type=stud_filter)
        if width_filter:
            products_qs = products_qs.filter(tire_spec__width=width_filter)
        if profile_filter:
            products_qs = products_qs.filter(tire_spec__profile=profile_filter)
        if diameter_filter:
            products_qs = products_qs.filter(tire_spec__diameter=diameter_filter)
        if load_index_filter:
            products_qs = products_qs.filter(tire_spec__load_index=load_index_filter)
        if speed_index_filter:
            products_qs = products_qs.filter(tire_spec__speed_index=speed_index_filter)

        filter_options = {
            "brands": Brand.objects.order_by("name"),
            "seasons": TireSpecification.Season.choices,
            "stud_types": TireSpecification.StudType.choices,
            "widths": TireSpecification.objects.exclude(width="").values_list("width", flat=True).distinct().order_by("width"),
            "profiles": TireSpecification.objects.exclude(profile="").values_list("profile", flat=True).distinct().order_by("profile"),
            "diameters": TireSpecification.objects.exclude(diameter="").values_list("diameter", flat=True).distinct().order_by("diameter"),
            "load_indices": TireSpecification.objects.exclude(load_index="").values_list("load_index", flat=True).distinct().order_by("load_index"),
            "speed_indices": TireSpecification.objects.exclude(speed_index="").values_list("speed_index", flat=True).distinct().order_by("speed_index"),
        }
    elif is_batteries:
        products_qs = Product.objects.select_related("brand", "category", "battery_spec").filter(
            product_type=Product.ProductType.BATTERIES,
            **base_filters,
        )
        brand_filter = request.GET.get("brand") or ""
        capacity_filter = request.GET.get("capacity_ah") or ""
        cca_filter = request.GET.get("cold_cranking_amps") or ""
        voltage_filter = request.GET.get("voltage") or ""
        polarity_filter = request.GET.get("polarity") or ""
        terminal_filter = request.GET.get("terminal_type") or ""
        length_filter = request.GET.get("length_mm") or ""
        width_filter = request.GET.get("width_mm") or ""
        height_filter = request.GET.get("height_mm") or ""

        if brand_filter:
            products_qs = products_qs.filter(brand_id=brand_filter)
        if capacity_filter:
            products_qs = products_qs.filter(battery_spec__capacity_ah=capacity_filter)
        if cca_filter:
            products_qs = products_qs.filter(battery_spec__cold_cranking_amps=cca_filter)
        if voltage_filter:
            products_qs = products_qs.filter(battery_spec__voltage=voltage_filter)
        if polarity_filter:
            products_qs = products_qs.filter(battery_spec__polarity=polarity_filter)
        if terminal_filter:
            products_qs = products_qs.filter(battery_spec__terminal_type=terminal_filter)
        if length_filter:
            products_qs = products_qs.filter(battery_spec__length_mm=length_filter)
        if width_filter:
            products_qs = products_qs.filter(battery_spec__width_mm=width_filter)
        if height_filter:
            products_qs = products_qs.filter(battery_spec__height_mm=height_filter)

        filter_options = {
            "brands": Brand.objects.order_by("name"),
            "capacities": BatterySpecification.objects.exclude(capacity_ah="").values_list("capacity_ah", flat=True).distinct().order_by("capacity_ah"),
            "ccas": BatterySpecification.objects.exclude(cold_cranking_amps="").values_list("cold_cranking_amps", flat=True).distinct().order_by("cold_cranking_amps"),
            "voltages": BatterySpecification.objects.exclude(voltage="").values_list("voltage", flat=True).distinct().order_by("voltage"),
            "polarities": BatterySpecification.objects.exclude(polarity="").values_list("polarity", flat=True).distinct().order_by("polarity"),
            "terminals": BatterySpecification.objects.exclude(terminal_type="").values_list("terminal_type", flat=True).distinct().order_by("terminal_type"),
            "lengths": BatterySpecification.objects.exclude(length_mm="").values_list("length_mm", flat=True).distinct().order_by("length_mm"),
            "widths": BatterySpecification.objects.exclude(width_mm="").values_list("width_mm", flat=True).distinct().order_by("width_mm"),
            "heights": BatterySpecification.objects.exclude(height_mm="").values_list("height_mm", flat=True).distinct().order_by("height_mm"),
        }
    elif is_parts:
        products_qs = Product.objects.select_related("brand", "category").prefetch_related("compatible_cars").filter(
            product_type=Product.ProductType.AUTO_PART,
            **base_filters,
        )
        brand_filter = request.GET.get("brand") or ""
        car_filter = request.GET.get("car") or ""
        price_min = request.GET.get("price_min") or ""
        price_max = request.GET.get("price_max") or ""

        if brand_filter:
            products_qs = products_qs.filter(brand_id=brand_filter)
        if car_filter:
            products_qs = products_qs.filter(compatible_cars__id=car_filter)
        if price_min:
            try:
                products_qs = products_qs.filter(price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                products_qs = products_qs.filter(price__lte=float(price_max))
            except ValueError:
                pass

        filter_options = {
            "brands": Brand.objects.order_by("name"),
            "cars": Car.objects.order_by("make", "model", "generation"),
        }
    else:
        filter_options = {}

    products = products_qs
    favorites_ids = set()
    if request.user.is_authenticated:
        favorites_ids = set(
            Favorite.objects.filter(customer__user=request.user).values_list("product_id", flat=True)
        )
    return render(
        request,
        "store/catalog.html",
        {
            "products": products,
            "selected_subcategory": selected_subcategory,
            "selected_main_category": main_category,
            "selected_main_category_label": selected_main_category_label,
            "is_rims": is_rims,
            "is_tires": is_tires,
            "is_parts": is_parts,
            "is_batteries": is_batteries,
            "rims_filters": filter_options if is_rims else {},
            "rims_selected": {
                "brand": brand_filter if is_rims else "",
                "diameter": diameter_filter if is_rims else "",
                "width": width_filter if is_rims else "",
                "pcd": pcd_filter if is_rims else "",
                "offset": offset_filter if is_rims else "",
                "center_bore": cb_filter if is_rims else "",
                "material": material_filter if is_rims else "",
                "color": color_filter if is_rims else "",
            } if is_rims else {},
            "tires_filters": filter_options if is_tires else {},
            "tires_selected": {
                "brand": brand_filter if is_tires else "",
                "season": season_filter if is_tires else "",
                "stud_type": stud_filter if is_tires else "",
                "width": width_filter if is_tires else "",
                "profile": profile_filter if is_tires else "",
                "diameter": diameter_filter if is_tires else "",
                "load_index": load_index_filter if is_tires else "",
                "speed_index": speed_index_filter if is_tires else "",
            } if is_tires else {},
            "batteries_filters": filter_options if is_batteries else {},
            "batteries_selected": {
                "brand": brand_filter if is_batteries else "",
                "capacity_ah": capacity_filter if is_batteries else "",
                "cold_cranking_amps": cca_filter if is_batteries else "",
                "voltage": voltage_filter if is_batteries else "",
                "polarity": polarity_filter if is_batteries else "",
                "terminal_type": terminal_filter if is_batteries else "",
                "length_mm": length_filter if is_batteries else "",
                "width_mm": width_filter if is_batteries else "",
                "height_mm": height_filter if is_batteries else "",
            } if is_batteries else {},
            "parts_filters": filter_options if is_parts else {},
            "parts_selected": {
                "brand": brand_filter if is_parts else "",
                "car": car_filter if is_parts else "",
                "price_min": price_min if is_parts else "",
                "price_max": price_max if is_parts else "",
            } if is_parts else {},
            "favorites_ids": favorites_ids,
        },
    )


@login_required
def favorites(request):
    favorites_qs = Favorite.objects.select_related("product", "customer").filter(
        customer__user=request.user
    )
    products = [f.product for f in favorites_qs]
    fav_ids = {f.product_id for f in favorites_qs}
    return render(request, "store/favorites.html", {"favorites": favorites_qs, "products": products, "favorites_ids": fav_ids})


@login_required
def toggle_favorite(request, product_id):
    next_url = request.GET.get("next") or request.POST.get("next") or request.META.get("HTTP_REFERER") or "catalog"
    product = get_object_or_404(Product, pk=product_id)
    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        customer = Customer.objects.create(user=request.user, phone=request.user.email, address=None)
    fav, created = Favorite.objects.get_or_create(customer=customer, product=product)
    if not created:
        fav.delete()
        _audit_log(essence=f"Favorite:{fav.pk}", action="remove_favorite", user=request.user)
        messages.info(request, "Товар удалён из избранного.")
    else:
        _audit_log(essence=f"Favorite:{fav.pk}", action="add_favorite", user=request.user)
        messages.success(request, "Товар добавлен в избранное.")
    return redirect(next_url)


def categories_view(request):
    return render(
        request,
        "store/categories.html",
        {"main_categories": MAIN_CATEGORY_CARDS},
    )


def category_detail_view(request, main_category):
    card = next((item for item in MAIN_CATEGORY_CARDS if item["key"] == main_category), None)
    if not card:
        raise Http404("Категория не найдена")

    subcategories = Category.objects.filter(main_category=main_category).order_by("name")
    groups = (
        CategoryGroup.objects.filter(main_category=main_category)
        .prefetch_related("categories")
        .order_by("order", "name")
    )
    grouped_ids = {
        category.id
        for group in groups
        for category in group.categories.all()
    }
    ungrouped_subcategories = subcategories.exclude(id__in=grouped_ids)

    return render(
        request,
        "store/category_detail.html",
        {
            "current_category": card,
            "groups": groups,
            "subcategories": ungrouped_subcategories,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Добро пожаловать в Drivee!"))
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})


@login_required
def profile_view(request):
    profile = getattr(request.user, "profile", None)
    vehicles = request.user.vehicles.select_related("car").order_by("-created_at")
    orders = (
        request.user.orders_requests.select_related("pickup_point")
        .order_by("-created_at")
    )
    vehicle_form = UserVehicleForm()
    profile_form = ProfileInfoForm(
        user=request.user,
        profile=profile,
        initial={
            "full_name": request.user.full_name,
            "email": request.user.email,
            "phone_number": getattr(profile, "phone_number", ""),
            "date_of_birth": getattr(profile, "date_of_birth", None),
        },
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_vehicle":
            vehicle_form = UserVehicleForm(request.POST)
            if vehicle_form.is_valid():
                vehicle = vehicle_form.save(commit=False)
                vehicle.user = request.user
                vehicle.save()
                messages.success(request, _("Автомобиль добавлен в профиль."))
                return redirect("profile")
            messages.error(request, _("Проверьте корректность данных автомобиля."))
        elif action == "update_profile":
            profile_form = ProfileInfoForm(request.POST, user=request.user, profile=profile)
            if profile_form.is_valid():
                request.user.full_name = profile_form.cleaned_data.get("full_name", "")
                request.user.email = profile_form.cleaned_data["email"]
                request.user.save(update_fields=["full_name", "email"])
                if profile is None:
                    profile, _created = UserProfile.objects.get_or_create(user=request.user)
                profile.phone_number = profile_form.cleaned_data.get("phone_number", "")
                profile.date_of_birth = profile_form.cleaned_data.get("date_of_birth")
                profile.save(update_fields=["phone_number", "date_of_birth"])
                messages.success(request, _("Профиль обновлён."))
                return redirect("profile")
            messages.error(request, _("Исправьте ошибки в форме профиля."))
        elif action == "delete_vehicle":
            vehicle_id = request.POST.get("vehicle_id")
            if vehicle_id:
                deleted, _unused = request.user.vehicles.filter(pk=vehicle_id).delete()
                if deleted:
                    messages.info(request, _("Автомобиль удалён."))
                else:
                    messages.warning(request, _("Автомобиль не найден."))
            else:
                messages.error(request, _("Не удалось определить автомобиль."))
            return redirect("profile")

    return render(
        request,
        "store/profile.html",
        {
            "profile": profile,
            "vehicles": vehicles,
            "vehicle_form": vehicle_form,
            "orders": orders,
            "profile_form": profile_form,
        },
    )


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(OrderRequest, pk=order_id, user=request.user)
    if request.method == "POST":
        if order.status in {"cancelled", "declined"}:
            messages.info(request, _("Заказ уже отменён."))
        else:
            order.status = "cancelled"
            order.save(update_fields=["status"])
            messages.info(request, _("Заказ отменён."))
    return redirect("profile")


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product", "product__brand", "product__category")
    total_cost = cart.total_cost()
    return render(
        request,
        "store/cart.html",
        {
            "cart": cart,
            "items": items,
            "total_cost": total_cost,
        },
    )


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        try:
            quantity = max(int(quantity), 1)
        except (TypeError, ValueError):
            quantity = 1

        available = product.stock_quantity
        next_url = request.POST.get("next") or "catalog"
        if available <= 0:
            messages.warning(request, _("Товар «%(name)s» временно отсутствует.") % {"name": product.name})
            return redirect(next_url)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )
        current_qty = 0 if created else cart_item.quantity
        max_addable = max(available - current_qty, 0)
        if max_addable <= 0:
            messages.warning(
                request,
                _("В корзине уже максимальное доступное количество для «%(name)s».") % {"name": product.name},
            )
            return redirect(next_url)

        if quantity > max_addable:
            quantity = max_addable
            messages.warning(
                request,
                _("Добавлено только %(qty)s шт. — больше нет в наличии.") % {"qty": quantity},
            )

        cart_item.quantity = current_qty + quantity
        cart_item.save()
        _audit_log(essence=f"CartItem:{cart_item.pk}", action="add_to_cart", user=request.user)
        messages.success(request, _("Товар добавлен в корзину."))

    return redirect(request.POST.get("next") or "catalog")


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("brand", "category")
        .select_related("tire_spec", "rim_spec", "battery_spec")
        .prefetch_related("compatible_cars", "auto_part_spec", "auto_goods_spec"),
        pk=pk,
    )
    related_products = (
        Product.objects.select_related("brand", "category")
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def brand_detail(request, pk):
    brand = get_object_or_404(
        Brand.objects.prefetch_related(
            "product_set__category",
            "product_set__compatible_cars",
        ),
        pk=pk,
    )
    total_products = brand.product_set.count()
    products = (
        brand.product_set.select_related("category")
        .prefetch_related("compatible_cars")
        .order_by("-stock_quantity", "name")[:5]
    )
    return render(
        request,
        "store/brand_detail.html",
        {
            "brand": brand,
            "products": products,
            "total_products": total_products,
        },
    )


@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items_qs = cart.items.select_related("product", "product__brand", "product__category")

    if not items_qs.exists():
        messages.info(request, _("Добавьте товары в корзину, чтобы оформить заказ."))
        return redirect("cart")
    items = list(items_qs)

    profile = getattr(request.user, "profile", None)
    initial_data = {
        "full_name": request.user.full_name or request.user.email,
        "email": request.user.email,
        "phone": getattr(profile, "phone_number", ""),
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
    else:
        form = CheckoutForm(initial=initial_data)

    pickup_points_qs = PickupPoint.objects.filter(is_active=True)
    form.fields["pickup_point"].queryset = pickup_points_qs

    if request.method == "POST" and form.is_valid():
        selected_pvz = form.cleaned_data.get("pickup_point")
        cart_snapshot = [
            {
                "product_id": item.product.id,
                "name": item.product.name,
                "quantity": item.quantity,
                "price": float(item.product.price),
                "line_total": float(item.line_total()),
            }
            for item in items
        ]

        insufficient = [
            item
            for item in items
            if item.quantity > item.product.stock_quantity
        ]
        if insufficient:
            for item in insufficient:
                messages.error(
                    request,
                    _("Товар «%(name)s» доступен только в количестве %(available)s шт.") % {
                        "name": item.product.name,
                        "available": item.product.stock_quantity,
                    },
                )
            return redirect("cart")

        product_ids = [item.product_id for item in items]
        try:
            with transaction.atomic():
                locked_products = {
                    p.id: p
                    for p in Product.objects.select_for_update().filter(id__in=product_ids)
                }
                order = OrderRequest.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    email=form.cleaned_data["email"],
                    delivery_type=form.cleaned_data["delivery_type"],
                    pickup_point=selected_pvz,
                    payment_method=form.cleaned_data["payment_method"],
                    comment=form.cleaned_data.get("comment", ""),
                    accept_terms=form.cleaned_data["accept_terms"],
                    cart_snapshot=cart_snapshot,
                    total_amount=cart.total_cost(),
                )

                for item in items:
                    product = locked_products.get(item.product_id)
                    if product is None or product.stock_quantity < item.quantity:
                        raise ValueError(
                            _("Товар «%(name)s» закончился. Обновите корзину.") % {"name": item.product.name}
                        )
                    product.stock_quantity -= item.quantity
                    product.save(update_fields=["stock_quantity"])
                cart.items.all().delete()
                _audit_log(essence=f"OrderRequest:{order.pk}", action="create_order", user=request.user)
                # Уведомление по email с номером заказа
                try:
                    send_mail(
                        subject=_("Ваш заказ #{id} принят").format(id=order.pk),
                        message=_(
                            "Спасибо за заказ!\n"
                            "Номер заказа: {id}\n"
                            "Сумма: {total} ₽\n"
                            "Мы свяжемся с вами для подтверждения."
                        ).format(id=order.pk, total=order.total_amount),
                        from_email=None,
                        recipient_list=[order.email],
                        fail_silently=True,
                    )
                except Exception as exc:
                    logger.exception("order email send failed #%s", order.pk, exc_info=exc)
        except ValueError as exc:
            messages.error(request, exc.args[0])
            return redirect("cart")

        messages.success(request, _("Заказ оформлен! Мы свяжемся с вами для подтверждения."))
        return redirect("home")

    total_cost = cart.total_cost()

    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "items": items,
            "total_cost": total_cost,
            "pickup_points": pickup_points_qs,
        },
    )


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        quantity = request.POST.get("quantity")
        try:
            quantity_value = int(quantity)
        except (TypeError, ValueError):
            messages.error(request, _("Некорректное количество."))
        else:
            available = cart_item.product.stock_quantity
            if available <= 0:
                cart_item.delete()
                messages.warning(
                    request,
                    _("Товара «%(name)s» больше нет на складе и он удалён из корзины.")
                    % {"name": cart_item.product.name},
                )
                return redirect("cart")
            if quantity_value > available:
                messages.warning(
                    request,
                    _("Максимум доступно %(available)s шт. для «%(name)s».")
                    % {"available": available, "name": cart_item.product.name},
                )
                quantity_value = available

            if quantity_value <= 0:
                cart_item.delete()
                messages.info(request, _("Товар удалён из корзины."))
                _audit_log(essence=f"CartItem:{cart_item.pk}", action="remove_from_cart", user=request.user)
            else:
                cart_item.quantity = quantity_value
                cart_item.save()
                _audit_log(essence=f"CartItem:{cart_item.pk}", action="update_cart", user=request.user)
                messages.success(request, _("Количество обновлено."))
    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    _audit_log(essence=f"CartItem:{cart_item.pk}", action="remove_from_cart", user=request.user)
    cart_item.delete()
    messages.info(request, _("Товар удалён из корзины."))
    return redirect("cart")
