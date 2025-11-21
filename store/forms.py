from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile, PickupPoint, UserVehicle, Car

User = get_user_model()


def _format_phone(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if not digits:
        return ""
    if digits.startswith("8"):
        digits = "7" + digits[1:]
    elif not digits.startswith("7"):
        digits = "7" + digits
    digits = (digits + "00000000000")[:11]
    return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"placeholder": "Повторите пароль"})
    )
    phone_number = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(attrs={
            "placeholder": "+7 (___) ___-__-__",
            "id": "phone_input"
        })
    )
    date_of_birth = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = User
        fields = ["full_name", "email"]
        labels = {
            "full_name": "Имя",
            "email": "Email"
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Введите имя"}),
            "email": forms.EmailInput(attrs={"placeholder": "Введите email"})
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "")
        formatted = _format_phone(phone)
        # Проверка бана по номеру
        from .models import UserProfile  # локальный импорт, чтобы избежать циклов
        if UserProfile.objects.filter(phone_number=formatted, user__is_banned=True).exists():
            raise forms.ValidationError("Этот номер заблокирован. Аккаунт недоступен.")
        return formatted

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "phone_number": self.cleaned_data.get("phone_number"),
                    "date_of_birth": self.cleaned_data.get("date_of_birth")
                }
            )
            if not created:
                profile.phone_number = self.cleaned_data.get("phone_number")
                profile.date_of_birth = self.cleaned_data.get("date_of_birth")
                profile.save(update_fields=["phone_number", "date_of_birth"])

        return user


class CheckoutForm(forms.Form):
    DELIVERY_CHOICES = (
        ("pickup", "Самовывоз со склада"),
        ("pvz", "Доставка в ПВЗ"),
    )

    PAYMENT_CHOICES = (
        ("card_now", "Картой сразу"),
        ("card_on_delivery", "Картой при получении"),
    )

    full_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={"placeholder": "Ваше имя"}))
    phone = forms.CharField(label="Телефон", widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"placeholder": "name@example.com"}))
    delivery_type = forms.ChoiceField(
        label="Тип доставки",
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect,
        initial="pickup",
    )
    pickup_point = forms.ModelChoiceField(
        label="Пункт выдачи",
        queryset=PickupPoint.objects.none(),
        required=False,
    )
    payment_method = forms.ChoiceField(
        label="Способ оплаты",
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial="card_now",
    )
    comment = forms.CharField(
        label="Комментарий к заказу",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Уточните детали доставки или пожелания"}),
        required=False,
    )
    accept_terms = forms.BooleanField(
        label="Я принимаю условия обработки персональных данных, доставки и соглашаюсь с офертой",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get("delivery_type")
        pickup_point = cleaned_data.get("pickup_point")

        if delivery_type == "pvz" and not pickup_point:
            self.add_error("pickup_point", "Выберите пункт выдачи на карте.")

        return cleaned_data


class UserVehicleForm(forms.ModelForm):
    class Meta:
        model = UserVehicle
        fields = ["car", "vin", "license_plate"]
        labels = {
            "car": "Автомобиль",
            "vin": "VIN",
            "license_plate": "Госномер",
        }
        widgets = {
            "vin": forms.TextInput(attrs={"placeholder": "Z94CB41AACR123456"}),
            "license_plate": forms.TextInput(attrs={"placeholder": "A123BC 799"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        car_field = self.fields.get("car")
        if car_field:
            car_field.queryset = Car.objects.order_by("make", "model", "generation")
            car_field.empty_label = "Выберите автомобиль"


class ProfileInfoForm(forms.Form):
    full_name = forms.CharField(
        label="Имя",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ваше имя"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    phone_number = forms.CharField(
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__"}),
    )
    date_of_birth = forms.DateField(
        label="Дата рождения",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = User.objects.exclude(pk=getattr(self.user, "pk", None)).filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "")
        if not phone:
            return ""
        return _format_phone(phone)
