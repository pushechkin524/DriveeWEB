from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

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
    OrderRequest,
    Brand,
    UserVehicle,
    UserProfile,
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


def home(request):
    daily_deals = DailyDeal.objects.select_related("product")[:6]
    return render(request, "store/home.html", {"daily_deals": daily_deals})


def catalog(request):
    subcategory_slug = request.GET.get("subcategory")
    main_category = request.GET.get("main_category")

    products_qs = (
        Product.objects.select_related("brand", "category")
        .filter(stock_quantity__gt=0)
    )
    selected_subcategory = None
    selected_main_category_label = None
    if subcategory_slug:
        selected_subcategory = get_object_or_404(Category, slug=subcategory_slug)
        products_qs = products_qs.filter(category=selected_subcategory)
    elif main_category:
        try:
            selected_main_category_label = Category.MainCategory(main_category).label
        except ValueError:
            raise Http404("Категория не найдена")
        products_qs = products_qs.filter(category__main_category=main_category)

    products = products_qs
    return render(
        request,
        "store/catalog.html",
        {
            "products": products,
            "selected_subcategory": selected_subcategory,
            "selected_main_category": main_category,
            "selected_main_category_label": selected_main_category_label,
        },
    )


@login_required
def favorites(request):
    favorites_qs = Favorite.objects.select_related("product", "customer").filter(
        customer__user=request.user
    )
    return render(request, "store/favorites.html", {"favorites": favorites_qs})


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
        messages.success(request, _("Товар добавлен в корзину."))

    return redirect(request.POST.get("next") or "catalog")


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("brand", "category")
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
            else:
                cart_item.quantity = quantity_value
                cart_item.save()
                messages.success(request, _("Количество обновлено."))
    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, _("Товар удалён из корзины."))
    return redirect("cart")
