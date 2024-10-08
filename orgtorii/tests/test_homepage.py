from unittest import skip

from .playwright import PlaywrightTestCase

# Persona:
# Jane is a curious developer who likes to try out new OrgTorii products.


@skip("Coming soon page is live")
class HomepageTestCase(PlaywrightTestCase):
    def test_homepage(self):
        # Jane hears of a new OrgTorii product and wants to check out the homepage
        context = self.browser.new_context()  # Create an isolated browser context
        page = context.new_page()
        page.goto(self.server_url)
        self.assertIn("Org Torii", page.title())
