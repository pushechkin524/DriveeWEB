from django import forms
from accounts.models import User, Role
from store.models import (
    Category,
    CategoryGroup,
    Product,
    OrderRequest,
    PickupPoint,
    AutoPartSpecification,
    AutoGoodsSpecification,
    Brand,
    Car,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "main_category", "group", "description"]


class CategoryGroupForm(forms.ModelForm):
    class Meta:
        model = CategoryGroup
        fields = ["name", "main_category", "order", "description"]


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "description", "image"]
        labels = {
            "name": "Название бренда",
            "description": "Описание",
            "image": "Изображение",
        }


class ProductBrandMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brand_field = self.fields.get("brand")
        if brand_field:
            brand_field.queryset = Brand.objects.order_by("name")
            brand_field.empty_label = "Без бренда"
        cars_field = self.fields.get("compatible_cars")
        if cars_field:
            cars_field.queryset = Car.objects.order_by("make", "model", "generation")
            cars_field.widget.attrs.setdefault("size", 8)
            cars_field.help_text = "Зажмите Cmd/Ctrl, чтобы выбрать несколько поколений."


class AutoPartProductForm(ProductBrandMixin):
    oem_number = forms.CharField(label="OEM / Оригинальный номер", required=False)
    manufacturer_article = forms.CharField(label="Артикул производителя", required=False)
    compatibility = forms.CharField(label="Доп. описание совместимости", required=False)
    installation_side = forms.CharField(label="Сторона установки", required=False)
    material = forms.CharField(label="Материал", required=False)
    weight_kg = forms.DecimalField(
        label="Вес, кг",
        required=False,
        max_digits=6,
        decimal_places=2,
    )
    dimensions = forms.CharField(label="Габариты (Д×Ш×В)", required=False)
    country_of_origin = forms.CharField(label="Страна производства", required=False)
    warranty = forms.CharField(label="Гарантия", required=False)
    certificates = forms.CharField(label="Сертификаты / Стандарты", required=False)

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock_quantity", "category", "brand", "image", "compatible_cars"]
        labels = {
            "name": "Название детали",
            "description": "Описание",
            "price": "Цена",
            "stock_quantity": "Количество на складе",
            "category": "Категория",
            "brand": "Бренд",
            "image": "Изображение",
            "compatible_cars": "Совместимые автомобили",
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        product.product_type = Product.ProductType.AUTO_PART
        if commit:
            product.save()
            self.save_m2m()
            AutoPartSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "oem_number": self.cleaned_data.get("oem_number", ""),
                    "manufacturer_article": self.cleaned_data.get("manufacturer_article", ""),
                    "compatibility": self.cleaned_data.get("compatibility", ""),
                    "installation_side": self.cleaned_data.get("installation_side", ""),
                    "material": self.cleaned_data.get("material", ""),
                    "weight_kg": self.cleaned_data.get("weight_kg"),
                    "dimensions": self.cleaned_data.get("dimensions", ""),
                    "country_of_origin": self.cleaned_data.get("country_of_origin", ""),
                    "warranty": self.cleaned_data.get("warranty", ""),
                    "certificates": self.cleaned_data.get("certificates", ""),
                },
            )
        return product


class AutoGoodsProductForm(ProductBrandMixin):
    article_code = forms.CharField(label="Артикул / Код", required=False)
    volume_or_weight = forms.CharField(label="Объём / Вес", required=False)
    size = forms.CharField(label="Размер (Д×Ш×В)", required=False)
    material = forms.CharField(label="Материал", required=False)
    color = forms.CharField(label="Цвет", required=False)
    compatibility = forms.CharField(label="Доп. описание совместимости", required=False)
    temperature_range = forms.CharField(label="Температурный диапазон", required=False)
    country_of_origin = forms.CharField(label="Страна производства", required=False)
    warranty = forms.CharField(label="Гарантия", required=False)
    package_contents = forms.CharField(label="Комплектация", required=False)

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock_quantity", "category", "brand", "image", "compatible_cars"]
        labels = {
            "name": "Название товара",
            "description": "Описание",
            "price": "Цена",
            "stock_quantity": "Количество на складе",
            "category": "Категория",
            "brand": "Бренд",
            "image": "Изображение",
            "compatible_cars": "Совместимые автомобили",
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        product.product_type = Product.ProductType.AUTO_GOODS
        if commit:
            product.save()
            self.save_m2m()
            AutoGoodsSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "article_code": self.cleaned_data.get("article_code", ""),
                    "volume_or_weight": self.cleaned_data.get("volume_or_weight", ""),
                    "size": self.cleaned_data.get("size", ""),
                    "material": self.cleaned_data.get("material", ""),
                    "color": self.cleaned_data.get("color", ""),
                    "compatibility": self.cleaned_data.get("compatibility", ""),
                    "temperature_range": self.cleaned_data.get("temperature_range", ""),
                    "country_of_origin": self.cleaned_data.get("country_of_origin", ""),
                    "warranty": self.cleaned_data.get("warranty", ""),
                    "package_contents": self.cleaned_data.get("package_contents", ""),
                },
            )
        return product


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["make", "model", "generation"]
        labels = {
            "make": "Марка",
            "model": "Модель",
            "generation": "Поколение",
        }


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = [
            "status",
            "delivery_type",
            "payment_method",
            "comment",
        ]


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Оставьте пустым, чтобы не менять пароль.",
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        label="Роль",
        empty_label=None,
    )

    class Meta:
        model = User
        fields = ["email", "full_name", "role", "is_active", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role_field = self.fields["role"]
        role_field.queryset = Role.objects.filter(role__in=Role.RoleName.values)
        role_field.label_from_instance = lambda obj: obj.get_role_display()

    def save(self, commit=True):
        password = self.cleaned_data.pop("password", "")
        user = super().save(commit=False)
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_password(User.objects.make_random_password())
        selected_role = self.cleaned_data.get("role")
        if selected_role:
            user.role = selected_role
            user.is_staff = selected_role.role == Role.RoleName.ADMIN
        else:
            user.is_staff = False
        if commit:
            user.save()
        return user


class PickupPointForm(forms.ModelForm):
    class Meta:
        model = PickupPoint
        fields = ["name", "company", "address", "working_hours", "description", "is_active"]
