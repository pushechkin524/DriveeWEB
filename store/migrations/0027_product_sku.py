from django.db import migrations, models
import string
import secrets


def generate_skus(apps, schema_editor):
    Product = apps.get_model("store", "Product")
    alphabet = string.ascii_uppercase + string.digits
    existing = set(Product.objects.exclude(sku__isnull=True).exclude(sku="").values_list("sku", flat=True))
    for product in Product.objects.all():
        if product.sku:
            existing.add(product.sku)
            continue
        for _ in range(30):
            candidate = "".join(secrets.choice(alphabet) for _ in range(6))
            if candidate in existing:
                continue
            product.sku = candidate
            product.save(update_fields=["sku"])
            existing.add(candidate)
            break


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0026_alter_product_product_type_batteryspecification"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.CharField(max_length=6, editable=False, null=True, blank=True, verbose_name="Артикул"),
        ),
        migrations.RunPython(generate_skus, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(max_length=6, editable=False, unique=True, verbose_name="Артикул"),
        ),
    ]
