from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from ..val import printinfo, get_webdriver


def torrent(url: str, conf) -> dict:
    b = get_webdriver(conf)
    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    # todo : implement

    b.quit()
    return info
