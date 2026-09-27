import pytest
from playwright.sync_api import Page, expect, Route


@pytest.fixture(autouse=True)
def track_and_block_submissions(page: Page):
    intercepted_posts = []

    def handle_route(route: Route):
        if route.request.method == "POST":
            url = route.request.url
            print(f"\n[VAROVÁNÍ] Aplikace se pokusila odeslat data na: {url}")
            intercepted_posts.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle_route)
    yield intercepted_posts


# Konstanty přesně odpovídající UI
ERR_NAME = "Full name must be at least 2 characters"
ERR_EMAIL = "Please enter a valid email address"
ERR_MSG = "Message must be at least 10 characters"


@pytest.mark.parametrize("scenario, name, email, message, expected_ui_errors", [
    # 1. Prázdný formulář - Úspěšně vyvolá všechny 3 chybové hlášky
    ("Empty Form", "", "", "", [ERR_NAME, ERR_EMAIL, ERR_MSG]),

    # 2. Hraniční hodnoty (Boundary Values)
    # 1 znak pro jméno a 9 znaků pro zprávu striktně poruší pravidlo "at least 2" a "at least 10"
    ("Too Short Inputs", "A", "spravny@email.cz", "123456789", [ERR_NAME, ERR_MSG]),

    # 3. Test JS e-mailové validace (Oklamání HTML5)
    # Tvar "test@localhost" projde přes nativní HTML5 (protože má zavináč),
    # ale moderní JS validátory ho zablokují, protože chybí koncovka (.cz/.com). Vykreslí se UI chyba.
    ("Invalid Email Domain", "Jan Novák", "test@localhost", "Dostatečně dlouhá zpráva", [ERR_EMAIL]),

    # --- SKUPINA B: Známé defekty (XFAIL - propouští bezpečnostní díry) ---
    pytest.param(
        "XSS Attack", "<script>alert(1)</script>", "hacker@test.com", "Dostatečně dlouhá zpráva", [],
        marks=pytest.mark.xfail(reason="Defekt: Aplikace propouští HTML/JS payloady a odesílá POST.")
    ),
    pytest.param(
        "Massive Payload", "Jan", "jan@test.com", "A" * 5000, [],
        marks=pytest.mark.xfail(reason="Defekt: Chybí omezení maxlength pro pole zprávy.")
    ),
])
def test_contact_form_ui_and_network_validation(
        page: Page,
        track_and_block_submissions: list,
        scenario: str, name: str, email: str, message: str, expected_ui_errors: list
):
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto("https://www.deafcom.org/contact")

    # 1. Vyplnění
    page.get_by_label("Full Name *").fill(name)
    page.get_by_label("Email Address *").fill(email)
    page.get_by_label("Message *").fill(message)

    # Odeslání
    page.get_by_role("button", name="Send Message").click()
    page.wait_for_timeout(500)

    # 2. Vizuální aserce UI
    for error_text in expected_ui_errors:
        error_locator = page.get_by_text(error_text)
        expect(
            error_locator,
            f"Očekávaná hláška '{error_text}' se nezobrazila pro scénář: {scenario}"
        ).to_be_visible(timeout=2000)

    # 3. Bezpečnostní aserce sítě
    assert len(track_and_block_submissions) == 0, (
        f"Frontend propustil data! Byl zachycen neplatný POST požadavek."
    )
