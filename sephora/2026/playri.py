from playwright.sync_api import sync_playwright


PRODUCT_URL = (
    "https://www.sephora.com/product/"
    "triclone-skin-tech-medium-coverage-foundation-with-fermented-arnica"
    "?skuId=2597276"
)


def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            viewport={
                "width": 1366,
                "height": 900,
            },
            locale="en-US",
        )

        page = context.new_page()

        def handle_response(response):

            url = response.url

            if (
                "/api/" in url
                or "product" in url.lower()
                or "catalog" in url.lower()
            ):

                print(
                    response.status,
                    response.request.method,
                    url
                )

        page.on(
            "response",
            handle_response
        )

        print("Opening product...")

        page.goto(
            PRODUCT_URL,
            wait_until="domcontentloaded",
            timeout=60_000
        )

        page.wait_for_timeout(10_000)

        print(
            "\nFinished. "
            "Browser will stay open."
        )

        page.wait_for_timeout(30_000)

        browser.close()


if __name__ == "__main__":
    main()