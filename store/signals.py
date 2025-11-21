import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .middleware import get_current_user
from .models import (
    AuditLog,
    CategoryGroup, Category, Brand, Product,
    AutoPartSpecification, AutoGoodsSpecification, TireSpecification, RimSpecification, BatterySpecification,
    Address, Customer, Order, PaymentMethod, Payment,
    AddressWH, Warehouse, Stock,
    Cart, CartItem, Favorite,
    PickupPoint, OrderRequest, DailyDeal,
    SparePartSection, SparePartItem,
    UserProfile, Car, UserVehicle,
)


TRACKED_MODELS = (
    CategoryGroup, Category, Brand, Product,
    AutoPartSpecification, AutoGoodsSpecification, TireSpecification, RimSpecification, BatterySpecification,
    Address, Customer, Order, PaymentMethod, Payment,
    AddressWH, Warehouse, Stock,
    PickupPoint, DailyDeal,
    SparePartSection, SparePartItem,
    UserProfile, Car, UserVehicle,
)

logger = logging.getLogger(__name__)


def _write_log(instance, action: str):
    if isinstance(instance, AuditLog):  # avoid recursion
        return
    user = get_current_user()
    _log_action(
        essence=f"{instance.__class__.__name__}:{getattr(instance, 'pk', None)}",
        action=action,
        user=user if getattr(user, "is_authenticated", False) else None,
    )


def _log_action(essence: str, action: str, user):
    try:
        AuditLog.objects.create(
            essence=essence,
            action=action,
            date=timezone.now(),
            user=user if getattr(user, "is_authenticated", False) else None,
        )
    except Exception as exc:
        logger.exception("Audit log write failed (%s / %s)", essence, action, exc_info=exc)


def _register_model(model):
    @receiver(post_save, sender=model, dispatch_uid=f"audit_save_{model.__name__}")
    def _on_save(sender, instance, created, **kwargs):
        _write_log(instance, "create" if created else "update")

    @receiver(post_delete, sender=model, dispatch_uid=f"audit_delete_{model.__name__}")
    def _on_delete(sender, instance, **kwargs):
        _write_log(instance, "delete")


for mdl in TRACKED_MODELS:
    _register_model(mdl)


# explicit signals for user-facing actions (favorites, cart, orders)
@receiver(post_save, sender=Favorite, dispatch_uid="audit_favorite_save")
def _favorite_saved(sender, instance, created, **kwargs):
    action = "add_favorite" if created else "update_favorite"
    user = getattr(instance.customer, "user", None) or get_current_user()
    _log_action(
        essence=f"Favorite:{instance.pk}",
        action=action,
        user=user,
    )


@receiver(post_delete, sender=Favorite, dispatch_uid="audit_favorite_delete")
def _favorite_deleted(sender, instance, **kwargs):
    user = getattr(instance.customer, "user", None) or get_current_user()
    _log_action(
        essence=f"Favorite:{instance.pk}",
        action="remove_favorite",
        user=user,
    )


@receiver(post_save, sender=CartItem, dispatch_uid="audit_cartitem_save")
def _cartitem_saved(sender, instance, created, **kwargs):
    action = "add_to_cart" if created else "update_cart"
    user = getattr(instance.cart, "user", None) or get_current_user()
    _log_action(
        essence=f"CartItem:{instance.pk}",
        action=action,
        user=user,
    )


@receiver(post_delete, sender=CartItem, dispatch_uid="audit_cartitem_delete")
def _cartitem_deleted(sender, instance, **kwargs):
    user = getattr(instance.cart, "user", None) or get_current_user()
    _log_action(
        essence=f"CartItem:{instance.pk}",
        action="remove_from_cart",
        user=user,
    )


@receiver(post_save, sender=OrderRequest, dispatch_uid="audit_order_created")
def _order_created(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.user or get_current_user()
    _log_action(
        essence=f"OrderRequest:{instance.pk}",
        action="create_order",
        user=user,
    )
import logging
