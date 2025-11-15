from django.db import migrations

ROLE_VALUES = (
    "user",
    "manager",
    "admin",
)

ALIAS_MAPPING = {
    "пользователь": "user",
    "user": "user",
    "customer": "user",
    "manager": "manager",
    "менеджер": "manager",
    "admin": "admin",
    "administrator": "admin",
    "админ": "admin",
    "администратор": "admin",
}


def normalize_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for role in Role.objects.all():
        value = (role.role or "").strip().lower()
        normalized = ALIAS_MAPPING.get(value)
        if normalized is None:
            normalized = "user"
        role.role = normalized
        role.save(update_fields=["role"])

    for code in ROLE_VALUES:
        Role.objects.get_or_create(role=code)


def reverse(apps, schema_editor):
    # Intentionally left blank: keeping normalized roles
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(normalize_roles, reverse),
    ]
