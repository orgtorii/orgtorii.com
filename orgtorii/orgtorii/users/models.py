from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class OrgToriiUser(AbstractUser):
    """Custom user model.

    As this can be hard to change mid project then we create a
    custom user model from the start.

    Read more: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#auth-custom-user"""

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    REQUIRED_FIELDS = []
