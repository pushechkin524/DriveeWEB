from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0021_brand_description_brand_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserVehicle",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("vin", models.CharField(blank=True, max_length=17, verbose_name="VIN")),
                ("license_plate", models.CharField(blank=True, max_length=16, verbose_name="Госномер")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="user_vehicles",
                        to="store.car",
                        verbose_name="Автомобиль",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vehicles",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Личный автомобиль",
                "verbose_name_plural": "Личные автомобили",
                "ordering": ["-created_at"],
            },
        ),
    ]
