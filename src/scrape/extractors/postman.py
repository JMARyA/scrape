from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from ..val import printinfo


def torrent(url: str, http_proxy: str) -> dict:
    options = {
        "proxy": {
            "http": http_proxy,
            "no_proxy": "localhost,127.0.0.1",
        }
    }
    b = webdriver.Chrome(seleniumwire_options=options)
    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    # todo : implement

    b.quit()
    return info
