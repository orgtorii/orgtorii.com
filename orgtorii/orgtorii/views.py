from django.shortcuts import redirect, render
from django.urls import reverse

from . import selectors


def homepage(request):
    return render(request, "orgtorii/homepage.html")


def register(request):
    if request.method == "POST":
        # Handle registration form submission
        return redirect(reverse("account:dashboard"))
    return render(request, "auth/register.html")


def dashboard(request):
    return render(request, "orgtorii/dashboard.html")


def pricing(request):
    products = selectors.product_list()
    return render(request, "orgtorii/pricing.html", {"products": products})
