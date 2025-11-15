from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0010_populate_category_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(
                blank=True,
                max_length=255,
                unique=True,
                verbose_name="Слаг",
            ),
        ),
    ]
