from collections.abc import Iterable

from djstripe.enums import ProductType
from djstripe.models import Product

from saas.users import models as user_models


def product_list() -> Iterable[Product]:
    """Return a list of Stripe products.

    Returns:
        Iterable[Product]: The list of products
    """
    return Product.objects.filter(type=ProductType.service)


def user_has_permission(*, user: user_models.User, permission: str) -> bool:
    """Check if a user has a specific permission.

    Args:
        user (user_models.User): an instance of the User model
        permission (str): the permission to check for

    Returns:
        bool: whether the user has the permission
    """
    return user.has_perm(permission)
