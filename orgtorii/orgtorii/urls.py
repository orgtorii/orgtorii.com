"""
URL configuration for orgtorii project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

from orgtorii.core import views as core_views

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("allauth.urls")),  # Django allauth
    path("stripe/", include("djstripe.urls", namespace="djstripe")),  # dj-stripe
    path("pricing/", views.pricing, name="pricing"),
    path(
        "newsletter/",
        include(
            (
                [
                    path("", core_views.newsletter_signup, name="signup"),
                    path("success", core_views.newsletter_success, name="signup_success"),
                ],
                "newsletter",
            ),
            namespace="newsletter",
        ),
    ),
    path(
        "",
        include(
            (
                [
                    path("coming-soon", core_views.coming_soon, name="coming_soon"),
                ],
                "core",
            ),
            namespace="core",
        ),
    ),
    path("", include("django_prometheus.urls")),
    path(
        "",
        include(
            ([path("dashboard", view=views.dashboard, name="dashboard")], "account"),
            namespace="account",
        ),
    ),
    path("", views.homepage, name="homepage"),
] + debug_toolbar_urls()
