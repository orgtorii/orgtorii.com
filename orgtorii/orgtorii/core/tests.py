import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from .forms import NewsletterSignupForm
from .models import NewsletterSignup


class NewsletterTestCase(TestCase):
    email = f"{uuid.uuid4()}@example.com"

    def test_newsletter_signup_uses_correct_template(self):
        response = self.client.get(reverse("newsletter:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/newsletter/signup.html")

    def test_newsletter_signup_uses_form(self):
        response = self.client.get(reverse("newsletter:signup"))
        self.assertIsInstance(response.context["form"], NewsletterSignupForm)

    def test_newsletter_signup_redirects_on_success(self):
        response = self.client.post(reverse("newsletter:signup"), {"email": self.email})
        self.assertRedirects(response, reverse("newsletter:signup_success"))

    def test_newsletter_signup_creates_signup(self):
        self.client.post(reverse("newsletter:signup"), {"email": self.email})
        self.assertTrue(NewsletterSignup.objects.filter(email=self.email).exists())

    def test_newsletter_signup_does_not_create_duplicate_signup(self):
        different_email = f"{uuid.uuid4()}@example.com"
        NewsletterSignup.objects.create(email=different_email)
        self.client.post(reverse("newsletter:signup"), {"email": different_email})
        self.assertEqual(NewsletterSignup.objects.filter(email=different_email).count(), 1)

    def test_newsletter_signup_shows_client_error_on_invalid_email(self):
        response = self.client.post(reverse("newsletter:signup"), {"email": "invalid-email"})
        self.assertContains(response, 'aria-invalid="true"')

    def test_newsletter_signup_shows_info_message_on_duplicate_email(self):
        email = f"{uuid.uuid4()}@example.com"
        NewsletterSignup.objects.create(email=email)
        response = self.client.post(reverse("newsletter:signup"), {"email": email})
        self.assertContains(response, escape(NewsletterSignupForm.ALREADY_SUBSCRIBED_ERROR))

    def test_newsletter_signup_shown_on_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/orgtorii/newsletter/signup.html")


class ComingSoonTestCase(TestCase):
    def test_coming_soon_page_uses_correct_template(self):
        response = self.client.get(reverse("core:coming_soon"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/coming_soon.html")

    def test_coming_soon_page_shows_message(self):
        response = self.client.get(reverse("core:coming_soon"))
        self.assertContains(response, "We're working on something new!")

    def test_coming_soon_page_shows_signup_form(self):
        response = self.client.get(reverse("core:coming_soon"))
        self.assertContains(response, 'id="newsletter-form"')
