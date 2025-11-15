from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Category = apps.get_model("store", "Category")
    for category in Category.objects.all():
        if category.slug:
            continue
        base_slug = slugify(category.name, allow_unicode=True) or f"category-{category.pk}"
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exclude(pk=category.pk).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        category.slug = slug
        category.save(update_fields=["slug"])


def reverse_slugs(apps, schema_editor):
    Category = apps.get_model("store", "Category")
    Category.objects.update(slug="")


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0009_alter_category_options_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_slugs),
    ]
