from selenium import webdriver
from selenium.webdriver.common.by import By
from ..val import printinfo


def torrent(url: str) -> dict:
    b = webdriver.Chrome()
    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    # todo : implement

    b.quit()
    return info
