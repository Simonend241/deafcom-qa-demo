import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.parametrize("link_name, expected_href, expected_url_pattern", [
    ("Home", "/", r"https://www\.deafcom\.org/?$"),
    ("Platform", "/platform", r".*/platform/?$"),
    ("Blog & Case Studies", "/blog", r".*/blog/?$"),
    ("Contact", "/contact", r".*/contact/?$"),
])
def test_desktop_main_menu_navigation(page: Page, link_name: str, expected_href: str, expected_url_pattern: str):
    """
    Ověřuje, že odkazy v hlavním menu jsou viditelné na desktopu,
    obsahují správný href atribut a po kliknutí přesměrují uživatele na správnou URL.
    """
    # 1. Příprava (Arrange)
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto("https://www.deafcom.org/")

    # 2. Akce & Assert DOM (Act & Assert)
    # OPRAVA: Omezujeme hledání pouze na element s rolí "navigation" (hlavní menu),
    # abychom ignorovali duplicitní odkazy v patičce a vyhnuli se Strict Mode violation.
    nav_link = page.get_by_role("navigation").get_by_role("link", name=link_name, exact=True)

    # Auto-retrying aserce
    expect(nav_link).to_be_visible()
    expect(nav_link).to_have_attribute("href", expected_href)

    # 3. Akce & Assert Navigace
    nav_link.click()

    expect(page).to_have_url(re.compile(expected_url_pattern))
