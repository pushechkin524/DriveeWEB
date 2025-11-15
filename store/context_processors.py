from .models import Cart


def cart_info(request):
    if not request.user.is_authenticated:
        return {"cart_item_count": 0}

    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        return {"cart_item_count": 0}

    return {
        "cart_item_count": cart.items.count(),
    }
