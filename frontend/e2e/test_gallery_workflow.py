import base64
import os
import time
import unittest
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright, expect


BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:5173")


def wait_for(url, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(1)
    raise TimeoutError(f"Service did not become ready: {url}")


class GalleryWorkflowE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wait_for("http://127.0.0.1:8000/api/auth/csrf/")
        wait_for(BASE_URL)
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(**self.playwright.devices["iPhone 13"])
        self.page = self.context.new_page()
        self.page.set_default_timeout(10000)
        self.page.set_default_navigation_timeout(15000)
        self.page.add_init_script("""try { Object.defineProperty(screen.orientation, 'type', { configurable: true, get: () => 'portrait-primary' }); } catch (_) {}""")
        self.page_errors = []
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    def tearDown(self):
        errors = self.page_errors
        self.context.close()
        self.assertEqual(errors, [], f"Browser JavaScript errors: {errors}")

    def test_complete_gallery_lifecycle(self):
        stamp = str(time.time_ns())
        username = f"e2e-gallery-{stamp}"
        password = "SecurePass123"
        gallery_name = "E2E Gallery"

        self.page.goto(f"{BASE_URL}/dashboard")
        expect(self.page).to_have_url(f"{BASE_URL}/login")

        self.page.goto(f"{BASE_URL}/signup")
        self.page.get_by_placeholder("Museum / Gallary name").fill(gallery_name)
        self.page.get_by_placeholder("username").fill(username)
        self.page.get_by_placeholder("email").fill(f"{username}@example.test")
        self.page.get_by_placeholder("password").fill(password)
        self.page.get_by_role("button", name="signup").click()

        expect(self.page).to_have_url(f"{BASE_URL}/additionalinfo")
        cookies = self.context.cookies()
        session = next((item for item in cookies if item["name"] == "gallery_session"), None)
        self.assertIsNotNone(session, "Signup must establish a gallery session cookie")
        self.assertTrue(session["httpOnly"], "Session cookie must be HttpOnly")
        self.assertIsNone(self.page.evaluate("() => localStorage.getItem('authToken')"))

        self.page.get_by_role("button", name="next").click()
        expect(self.page).to_have_url(f"{BASE_URL}/dashboard")
        expect(self.page.get_by_text(gallery_name)).to_be_visible()

        self.page.get_by_role("button", name="add new item").click()
        expect(self.page).to_have_url(f"{BASE_URL}/additem")
        self.page.get_by_placeholder("Title").fill("E2E artwork")
        image = self.page.locator('input[type="file"]').first
        image.set_input_files({
            "name": "target.png",
            "mimeType": "image/png",
            "buffer": base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8z8DAwMDAxMDAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg=="
            ),
        })
        self.page.get_by_role("button", name="Done").click()
        expect(self.page).to_have_url(f"{BASE_URL}/dashboard")

        self.page.get_by_role("button", name="library").click()
        expect(self.page.get_by_text("E2E artwork")).to_be_visible()
        self.page.get_by_text("E2E artwork").click()
        expect(self.page).to_have_url(f"{BASE_URL}/editItem")
        self.page.get_by_placeholder("Title").fill("Updated art")
        self.page.get_by_role("button", name="Done").click()
        expect(self.page).to_have_url(f"{BASE_URL}/library")
        expect(self.page.get_by_text("Updated art")).to_be_visible()

        self.page.get_by_text("Updated art").click()
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_role("button", name="Delete Item").click()
        expect(self.page).to_have_url(f"{BASE_URL}/library")
        expect(self.page.get_by_text("Updated art")).to_have_count(0)

        self.page.goto(f"{BASE_URL}/dashboard")
        self.page.get_by_role("button", name="logout").click()
        expect(self.page).to_have_url(f"{BASE_URL}/login")

        self.page.get_by_placeholder("username").fill(username)
        self.page.get_by_placeholder("password").fill(password)
        self.page.get_by_role("button", name="login").click()
        expect(self.page).to_have_url(f"{BASE_URL}/dashboard")
        expect(self.page.get_by_text(gallery_name)).to_be_visible()

        renewed = next(
            (item for item in self.context.cookies() if item["name"] == "gallery_session"),
            None,
        )
        self.assertIsNotNone(renewed, "Login must establish a new session cookie")
        self.assertTrue(renewed["httpOnly"])
        self.assertIsNone(self.page.evaluate("() => localStorage.getItem('authToken')"))

        self.page.get_by_role("button", name="logout").click()
        expect(self.page).to_have_url(f"{BASE_URL}/login")
        self.assertFalse(
            any(item["name"] == "gallery_session" for item in self.context.cookies()),
            "Logout must clear the session cookie",
        )

    def test_invalid_login_displays_error_without_authenticating(self):
        self.page.goto(f"{BASE_URL}/login")
        self.page.get_by_placeholder("username").fill(f"missing-{time.time_ns()}")
        self.page.get_by_placeholder("password").fill("WrongPassword123")
        self.page.get_by_role("button", name="login").click()
        expect(self.page.get_by_text("Invalid username or password.")).to_be_visible()
        expect(self.page).to_have_url(f"{BASE_URL}/login")


if __name__ == "__main__":
    unittest.main(verbosity=2)
