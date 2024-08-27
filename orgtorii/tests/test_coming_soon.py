from django.urls import reverse

from .playwright import PlaywrightTestCase

# Persona:
# Howie is curious about the new OrgTorii product and wants to learn more about what it is.


class ComingSoonTestCase(PlaywrightTestCase):
    email = "howie@example.com"

    def test_coming_soon(self):
        # Howie wants to learn more about the new OrgTorii product
        context = self.browser.new_context()
        context.set_default_timeout(1000)
        page = context.new_page()

        # He goes to the homepage
        page.goto(self.server_url)
        self.assertIn("Coming Soon", page.title())

        # He sees a message about the product being in development
        self.expect(page).to_have_text("We're working on something new!")

        # He sees a form to sign up for updates
        self.expect(page).to_have_selector("form#newsletter-form")

        # He enters his email address and submits the form
        newsletter_form = page.locator("form#newsletter-form")
        email_input = newsletter_form.locator("input[name=email]")
        email_input.type(self.email)
        newsletter_form.locator("button[type=submit]").click()

        # He sees a confirmation message that he has signed up for updates
        page.wait_for_url(self.server_url + reverse("newsletter:signup_success"), timeout=500)
        self.expect(page).to_have_text("You're signed up for updates")

        # Howie then tries to break the system a bit and go to other URLs
        page.goto(self.server_url + "/login")

        # He is redirected back to the homepage
        page.wait_for_url(self.server_url, timeout=500)
        self.expect(page).to_have_url(self.server_url)

        # So he closes his browser and waits for updates
        page.close()

    def test_submit_early_review_form(self):
        # Howie wants to submit an early review of his previous or current employers
        context = self.browser.new_context()
        page = context.new_page()

        # He goes to the homepage
        page.goto(self.server_url)

        # He sees a form to submit a simple review

        # He enters his name, the review, his employer details and the rating

        # He submits the form

        # He sees a confirmation message that his review has been submitted
        pass
