import factory
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from djstripe.enums import PriceType, ProductType
from djstripe.models import Price, Product

User = get_user_model()


###############################################
## Factory boy model factories
###############################################
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: "%d" % n)
    name = factory.Faker("word")
    type = ProductType.service


class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Price

    id = factory.Sequence(lambda n: "%d" % n)
    active = True
    currency = "usd"
    product = factory.SubFactory(ProductFactory)
    type = PriceType.recurring
    unit_amount = factory.Faker("random_int", min=1000, max=10000)
    nickname = factory.Faker("word")


###############################################
## Test cases
###############################################
class HomepageTestCase(TestCase):
    def test_uses_home_template(self):
        response = self.client.get(reverse("homepage"))
        self.assertTemplateUsed(response, "orgtorii/homepage.html")


class AuthTestCase(TestCase):
    email = "jane@example.com"
    password = "iKDt6EFwyQEjkgqSzCdvFdC7imS5JN0H"

    def test_register_view_uses_template(self):
        response = self.client.get(reverse("account_signup"))

        self.assertTemplateUsed(response, "account/signup.html")

    def test_register_successfully_registers_user(self):
        form_data = {"email": self.email, "password1": self.password}

        self.client.post(
            reverse("account_signup"),
            data=form_data,
        )

        users = User.objects.filter(email=self.email)
        self.assertEqual(users.count(), 1)

    def test_register_redirects_on_valid_data(self):
        form_data = {"email": self.email, "password1": self.password}

        response = self.client.post(
            reverse("account_signup"),
            data=form_data,
        )

        self.assertRedirects(response, reverse("account_email_verification_sent"))

    def test_register_shows_error_on_invalid_password(self):
        form_data = {"email": self.email, "password1": ""}

        response = self.client.post(
            reverse("account_signup"),
            data=form_data,
        )

        self.assertTemplateUsed(response, "account/signup.html")
        self.assertContains(response, "This field is required")

    def test_register_shows_error_on_invalid_email(self):
        form_data = {"email": "invalid-email", "password1": self.password}

        response = self.client.post(
            reverse("account_signup"),
            data=form_data,
        )

        self.assertTemplateUsed(response, "account/signup.html")
        self.assertContains(response, "Enter a valid email address")

    def test_dashboard_view(self):
        response = self.client.get(reverse("account:dashboard"))

        self.assertTemplateUsed(response, "orgtorii/dashboard.html")


class PricingTestCase(TestCase):
    def test_uses_pricing_template(self):
        response = self.client.get(reverse("pricing"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orgtorii/pricing.html")

    def test_pricing_view_returns_products(self):
        ProductFactory()
        ProductFactory()

        response = self.client.get(reverse("pricing"))

        self.assertIn("products", response.context)
        self.assertIsNotNone(response.context["products"])
        self.assertEqual(len(response.context["products"]), 2)

    def test_pricing_view_only_shows_service_products(self):
        ProductFactory(type=ProductType.good)
        service = ProductFactory(type=ProductType.service)

        response = self.client.get(reverse("pricing"))

        self.assertEqual(len(response.context["products"]), 1)
        self.assertEqual(response.context["products"][0].type, ProductType.service)
        self.assertEqual(response.context["products"][0].name, service.name)

    def test_pricing_view_shows_price_details(self):
        product = ProductFactory()
        PriceFactory(product=product)
        PriceFactory(product=product)

        response = self.client.get(reverse("pricing"))

        self.assertIn("products", response.context)
        self.assertIsNotNone(response.context["products"])
        self.assertEqual(len(response.context["products"]), 1)

        product = response.context["products"][0]

        self.assertIsNotNone(product.prices)
        self.assertEqual(product.prices.count(), 2)
