from django.shortcuts import redirect, render
from meta.views import Meta

from .forms import NewsletterSignupForm


def newsletter_signup(request):
    form = NewsletterSignupForm()
    meta = Meta(title="Newsletter Signup")

    if request.method == "POST":
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("newsletter:signup_success")
    return render(request, "core/pages/newsletter/signup.html", {"form": form, "meta": meta})


def newsletter_success(request):
    meta = Meta(title="Thank you")
    return render(request, "core/pages/newsletter/success.html", {"meta": meta})


def coming_soon(request):
    meta = Meta(title="Org Torii - Coming Soon")
    newsletter_form = NewsletterSignupForm()

    return render(
        request, "core/coming_soon.html", {"meta": meta, "newsletter_form": newsletter_form}
    )
