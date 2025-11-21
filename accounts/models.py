from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)


class Role(models.Model):
    class RoleName(models.TextChoices):
        USER = ("user", "Пользователь")
        MANAGER = ("manager", "Менеджер")
        ADMIN = ("admin", "Администратор")

    role_id = models.BigAutoField(primary_key=True)
    role = models.CharField(
        max_length=255,
        unique=True,
        choices=RoleName.choices,
    )

    def __str__(self):
        return self.get_role_display()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def role_code(self):
        return getattr(self.role, "role", None)

    def is_admin_role(self):
        if self.is_superuser:
            return True
        return self.role_code == Role.RoleName.ADMIN

    def is_manager_role(self):
        return self.role_code == Role.RoleName.MANAGER
