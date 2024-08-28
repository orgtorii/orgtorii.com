import uuid
from sqlite3 import IntegrityError

from django.forms import ValidationError
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
        company_domain = Faker("domain_name")
        job_title = Faker("job")
        location = Faker("address")
        estimated_review_date = Faker("date")
        tenure_months = Faker("random_int", min=1, max=120)
        current_employee = Faker("boolean")
        review_title = Faker("sentence", nb_words=10)
        review = Faker("paragraph", nb_sentences=50)
        culture_rating = Faker("random_int", min=1, max=5)
        work_life_balance_rating = Faker("random_int", min=1, max=5)
        leadership_rating = Faker("random_int", min=1, max=5)
        opportunities_rating = Faker("random_int", min=1, max=5)
        compensation_rating = Faker("random_int", min=1, max=5)
        pros = []
        cons = []
        base_annual_salary = Faker("random_int", min=5_000, max=900_000)
        additional_annual_compensation = Faker("random_int", min=0, max=10_000)
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

    def test_filename_generation_sanitization(self):
        review = self.Factory()
        upload_path = core_models.get_payslip_upload_path(review, "payslip with spaces.pdf")
        self.assertNotIn(" ", upload_path)
        self.assertTrue(upload_path.endswith("payslip_with_spaces.pdf"))
        self.assertTrue(upload_path.startswith("employer_reviews/payslips/"))

    def test_review_cannot_be_too_short(self):
        review = self.Factory(review=Faker("text", max_nb_chars=159))
        with self.assertRaises(ValidationError) as cm:
            review.full_clean()
        self.assertIn(
            f"Ensure this value has at least 160 characters (it has {len(review.review)}).",
            cm.exception.messages,
        )
        self.assertEqual(len(cm.exception.error_dict), 1)

    def test_review_cannot_be_in_the_future(self):
        review = self.Factory.build(estimated_review_date=Faker("future_date"))
        with self.assertRaises(ValidationError) as cm:
            review.full_clean()
        self.assertIn("The date cannot be in the future.", cm.exception.messages)
        self.assertEqual(len(cm.exception.error_dict), 1)

    def test_review_title_cannot_be_too_short(self):
        review = self.Factory(review_title=Faker("text", max_nb_chars=9))
        with self.assertRaises(ValidationError) as cm:
            review.full_clean()
        self.assertIn(
            f"Ensure this value has at least 10 characters (it has {len(review.review_title)}).",
            cm.exception.messages,
        )
        self.assertEqual(len(cm.exception.error_dict), 1)

    def test_company_domain_name_not_required(self):
        review = self.Factory(company_domain="")
        review.full_clean()

    def test_default_pros_cons_are_empty_list(self):
        review = self.Factory()
        review.full_clean()
        self.assertEqual(review.pros, [])
        self.assertEqual(review.cons, [])

    def test_pros_are_saved_as_list(self):
        review = self.Factory(pros=["Great team", "Good work-life balance"])
        review.full_clean()
        self.assertEqual(review.pros, ["Great team", "Good work-life balance"])
        review = core_models.EmployerReviewMVP.objects.get(pk=review.pk)
        self.assertEqual(review.pros, ["Great team", "Good work-life balance"])

    def test_cons_are_saved_as_list(self):
        review = self.Factory(cons=["Bad management", "Low pay"])
        review.full_clean()
        self.assertEqual(review.cons, ["Bad management", "Low pay"])
        review = core_models.EmployerReviewMVP.objects.get(pk=review.pk)
        self.assertEqual(review.cons, ["Bad management", "Low pay"])

    def test_negative_salary_is_not_allowed(self):
        review = self.Factory(base_annual_salary=-1)
        with self.assertRaises(IntegrityError) as cm:
            review.full_clean()
        print(cm.exception)

    def test_no_salary_is_allowed(self):
        review = self.Factory(base_annual_salary=0)
        review.full_clean()

    def test_negative_additional_annual_compensation_is_not_allowed(self):
        review = self.Factory(additional_annual_compensation=-1)
        with self.assertRaises(IntegrityError) as cm:
            review.full_clean()
        print(cm.exception)
