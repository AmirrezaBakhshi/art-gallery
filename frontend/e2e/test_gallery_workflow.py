import io
import os
import time
import unittest
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright, expect


BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:5173")
SHOWCASE_DIR = Path(os.getenv("SHOWCASE_DIR", "docs/showcase"))


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


def demo_image_bytes(size=(900, 1200), avatar=False):
    """Generate original, deterministic sample imagery for the showcase."""
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            blend = (x / max(width - 1, 1) * 0.55) + (y / max(height - 1, 1) * 0.45)
            pixels[x, y] = (
                int(24 + 48 * blend),
                int(31 + 74 * (1 - blend)),
                int(48 + 92 * blend),
            )

    draw = ImageDraw.Draw(image, "RGBA")
    if avatar:
        draw.ellipse((70, 70, width - 70, height - 70), fill=(218, 179, 125, 245))
        draw.ellipse((145, 145, width - 145, height - 145), fill=(29, 42, 62, 255))
        draw.arc((165, 165, width - 165, height - 165), 200, 520, fill=(232, 205, 160, 255), width=18)
    else:
        draw.ellipse((120, 210, 760, 850), fill=(217, 145, 92, 210))
        draw.ellipse((245, 330, 650, 740), fill=(32, 52, 77, 230))
        draw.polygon(
            [(80, 930), (390, 500), (820, 1010), (760, 1130), (150, 1100)],
            fill=(222, 190, 143, 225),
        )
        draw.arc((170, 250, 760, 940), 205, 510, fill=(246, 220, 178, 255), width=22)
        draw.line((130, 1040, 770, 160), fill=(255, 255, 255, 115), width=8)

    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()

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
        self.capture_showcase = (
            os.getenv("CAPTURE_SHOWCASE") == "1"
            and self._testMethodName == "test_complete_gallery_lifecycle"
        )
        context_options = dict(self.playwright.devices["iPhone 13"])
        if self.capture_showcase:
            (SHOWCASE_DIR / "screenshots").mkdir(parents=True, exist_ok=True)
            (SHOWCASE_DIR / "videos").mkdir(parents=True, exist_ok=True)
            context_options["record_video_dir"] = str(SHOWCASE_DIR / "videos")

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        self.video = self.page.video
        self.page.set_default_timeout(10000)
        self.page.set_default_navigation_timeout(15000)
        self.page.add_init_script(
            """try { Object.defineProperty(screen.orientation, 'type', { configurable: true, get: () => 'portrait-primary' }); } catch (_) {}"""
        )
        self.page_errors = []
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    def pause_for_showcase(self, milliseconds=1100):
        if self.capture_showcase:
            self.page.wait_for_timeout(milliseconds)

    def capture(self, filename):
        if self.capture_showcase:
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(500)
            self.page.screenshot(
                path=str(SHOWCASE_DIR / "screenshots" / filename),
                full_page=True,
                animations="disabled",
            )

    def tearDown(self):
        errors = self.page_errors
        self.context.close()
        if self.capture_showcase and self.video:
            self.video.save_as(str(SHOWCASE_DIR / "videos" / "artgallery-walkthrough.webm"))
            Path(self.video.path()).unlink(missing_ok=True)
        self.assertEqual(errors, [], f"Browser JavaScript errors: {errors}")

    def test_complete_gallery_lifecycle(self):
        stamp = str(time.time_ns())
        username = f"e2e-gallery-{stamp}"
        password = "SecurePass123"
        gallery_name = "Atelier North Gallery"

        self.page.goto(BASE_URL)
        self.capture("01-home.png")
        expect(self.page.get_by_text("Do you own a museum / gallary?")).to_be_visible()

        self.page.goto(f"{BASE_URL}/signup")
        self.pause_for_showcase()
        self.capture("02-signup.png")
        self.page.get_by_placeholder("Museum / Gallary name").fill(gallery_name)
        self.page.get_by_placeholder("username").fill(username)
        self.page.get_by_placeholder("email").fill(f"{username}@example.test")
        self.page.get_by_placeholder("password").fill(password)
        self.page.get_by_role("button", name="signup").click()

        expect(self.page).to_have_url(f"{BASE_URL}/additionalinfo")
        if self.capture_showcase:
            self.page.locator('input[type="file"]').first.set_input_files({
                "name": "atelier-avatar.png",
                "mimeType": "image/png",
                "buffer": demo_image_bytes((600, 600), avatar=True),
            })
            self.page.locator("textarea").nth(0).fill("A contemporary space for thoughtful art, material studies, and emerging creative voices.")
            self.page.locator("textarea").nth(1).fill("12 Gallery Lane")
            self.page.locator('input[type="number"]').fill("5550102040")
        self.pause_for_showcase(1300)
        self.capture("03-gallery-setup.png")
        cookies = self.context.cookies()
        session = next((item for item in cookies if item["name"] == "gallery_session"), None)
        self.assertIsNotNone(session, "Signup must establish a gallery session cookie")
        self.assertTrue(session["httpOnly"], "Session cookie must be HttpOnly")
        self.assertIsNone(self.page.evaluate("() => localStorage.getItem('authToken')"))

        self.page.get_by_role("button", name="next").click()
        expect(self.page).to_have_url(f"{BASE_URL}/dashboard")
        expect(self.page.get_by_text(gallery_name)).to_be_visible()
        self.pause_for_showcase(1400)
        self.capture("04-gallery-dashboard.png")

        self.page.get_by_role("button", name="add new item").click()
        expect(self.page).to_have_url(f"{BASE_URL}/additem")
        self.page.get_by_placeholder("Title").fill("Form Study 01")
        self.page.locator("textarea").fill("An exploration of geometry, balance, and warm natural forms. Original mixed-media study created for the Atelier North collection.")
        self.page.locator('input[type="file"]').first.set_input_files({
            "name": "study-in-form.png",
            "mimeType": "image/png",
            "buffer": demo_image_bytes(),
        })
        self.pause_for_showcase(1400)
        self.capture("05-artwork-editor.png")
        self.page.get_by_role("button", name="Done").click()
        expect(self.page).to_have_url(f"{BASE_URL}/dashboard")

        self.page.get_by_role("button", name="library").click()
        expect(self.page.get_by_text("Form Study 01")).to_be_visible()
        self.pause_for_showcase(1300)
        self.capture("06-gallery-library.png")

        self.page.goto(f"{BASE_URL}/iteminfo/0")
        expect(self.page.get_by_text("Form Study 01")).to_be_visible()
        artwork_image = self.page.locator('img[src*="target_images"]')
        expect(artwork_image).to_be_visible()
        artwork_image.evaluate("(image) => image.decode()")
        self.pause_for_showcase(1400)
        self.capture("07-public-artwork.png")
        self.page.get_by_role("button", name="view museum / gallary info").click()
        expect(self.page.get_by_text(gallery_name)).to_be_visible()
        self.pause_for_showcase(1400)
        self.capture("08-public-gallery-profile.png")

        self.page.goto(f"{BASE_URL}/dashboard")
        self.page.get_by_role("button", name="library").click()
        self.page.get_by_text("Form Study 01").click()
        expect(self.page).to_have_url(f"{BASE_URL}/editItem")
        self.page.get_by_placeholder("Title").fill("Updated Study")
        self.page.get_by_role("button", name="Done").click()
        expect(self.page).to_have_url(f"{BASE_URL}/library")
        expect(self.page.get_by_text("Updated Study")).to_be_visible()

        self.page.get_by_text("Updated Study").click()
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_role("button", name="Delete Item").click()
        expect(self.page).to_have_url(f"{BASE_URL}/library")
        expect(self.page.get_by_text("Updated Study")).to_have_count(0)

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
