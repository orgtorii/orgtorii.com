from .playwright import PlaywrightTestCase

# Persona:
# Jane is a curious developer who likes to try out new SaaS products.


class HomepageTestCase(PlaywrightTestCase):
    def test_homepage(self):
        # Jane hears of a new SaaS product and wants to check out the homepage
        context = self.browser.new_context()  # Create an isolated browser context
        page = context.new_page()
        page.goto(self.live_server_url)
        self.assertIn("SaaS Kit", page.title())
