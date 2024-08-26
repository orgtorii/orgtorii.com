from unittest import skip

from django.urls import reverse

from .playwright import PlaywrightTestCase

# Persona:
# Andy is a user who wants to log in to the OrgTorii product to access their account.


@skip("Skip until the test is implemented")
class AuthenticationTestCase(PlaywrightTestCase):
    user_email = "andy@example.com"
    user_password = "iKDt6EFwyQEjkgqSzCdvFdC7imS5JN0H"

    def test_user_auth_flow(self):
        # Andy wants to register for the OrgTorii product
        context = self.browser.new_context()
        context.set_default_timeout(3000)
        page = context.new_page()

        # After they visit the homepage, they click on the "Sign Up" link
        page.goto(self.live_server_url)
        page.locator("a", has_text="Sign Up").click()

        # They are taken to the registration page
        page.wait_for_url(self.live_server_url + reverse("auth:register"))
        self.assertIn("Sign Up", page.title())

        # They fill in the registration form with their details
        page.locator('input[name="email"]').fill(self.user_email)
        page.locator('input[name="password"]').fill(self.user_password)

        # They click the "Sign Up" button
        page.locator("button", has_text="Sign Up").click()

        # Upon successful registration, they are redirected to their account page
        page.wait_for_url(self.live_server_url + reverse("account:dashboard"), timeout=3000)

        # After looking at their account, they log out
        page.locator("a", has_text="Log Out").click()

        # They are redirected to the login page
        page.wait_for_url(self.live_server_url + reverse("auth:login"))

        # They fill in the login form with their details
        page.locator('input[name="email"]').fill(self.user_email)
        page.locator('input[name="password"]').fill(self.user_password)

        # They click the "Sign In" button
        page.locator("button", has_text="Sign In").click()

        # They are redirected to their account page
        page.wait_for_url(self.live_server_url + reverse("account:dashboard"))

        # After looking at their account, they log out
        page.locator("a", has_text="Log Out").click()

        # They are redirected to the login page
        page.wait_for_url(self.live_server_url + reverse("auth:login"))

        # Unfortunately they have already forgotten their password
        # so they start the password recovery process by clicking the "Forgot Password" link
        page.locator("a", has_text="Forgot Password").click()
        page.wait_for_url(self.live_server_url + reverse("auth:password_reset"))
        page.locator('input[name="email"]').fill(self.user_email)
        page.locator("button", has_text="Send Reset Link").click()
