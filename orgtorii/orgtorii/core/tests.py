import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from factory.django import DjangoModelFactory
from factory.faker import Faker

from . import models as core_models
from .forms import NewsletterSignupForm


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
        self.assertTrue(core_models.NewsletterSignup.objects.filter(email=self.email).exists())

    def test_newsletter_signup_does_not_create_duplicate_signup(self):
        different_email = f"{uuid.uuid4()}@example.com"
        core_models.NewsletterSignup.objects.create(email=different_email)
        self.client.post(reverse("newsletter:signup"), {"email": different_email})
        self.assertEqual(
            core_models.NewsletterSignup.objects.filter(email=different_email).count(), 1
        )

    def test_newsletter_signup_shows_client_error_on_invalid_email(self):
        response = self.client.post(reverse("newsletter:signup"), {"email": "invalid-email"})
        self.assertContains(response, 'aria-invalid="true"')

    def test_newsletter_signup_shows_info_message_on_duplicate_email(self):
        email = f"{uuid.uuid4()}@example.com"
        core_models.NewsletterSignup.objects.create(email=email)
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


class EmployerReviewMVPTestCase(TestCase):
    class Factory(DjangoModelFactory):
        class Meta:
            model = core_models.EmployerReviewMVP

        company_name = Faker("company")
        company_url = Faker("url")
        job_title = Faker("job")
        location = Faker("address")
        estimated_review_date = Faker("date")
        tenure_months = Faker("random_int", min=1, max=120)
        current_employee = Faker("boolean")
        review_title = Faker("sentence")
        review = Faker("text")
        culture_rating = Faker("random_int", min=1, max=5)
        work_life_balance_rating = Faker("random_int", min=1, max=5)
        leadership_rating = Faker("random_int", min=1, max=5)
        opportunities_rating = Faker("random_int", min=1, max=5)
        compensation_rating = Faker("random_int", min=1, max=5)
        pros = list()
        cons = list()
        verified = Faker("boolean")

    def test_typeid_generation(self):
        review = self.Factory()
        upload_path = core_models.get_payslip_upload_path(review, "payslip.pdf")
        self.assertEqual(len(upload_path.split("/")), 4)
        another_upload_path_with_same_filename = core_models.get_payslip_upload_path(
            review, "payslip.pdf"
        )
        self.assertNotEqual(upload_path, another_upload_path_with_same_filename)

    def test_filename_generation_length(self):
        review = self.Factory()
        upload_path = core_models.get_payslip_upload_path(review, f"{'payslip'*30}.pdf")
        self.assertLessEqual(len(upload_path), 100)
