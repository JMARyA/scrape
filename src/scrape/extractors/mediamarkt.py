from selenium.webdriver.common.by import By
from selenium.common import exceptions
import re
from ..val import (
    get_webdriver,
    scrollToElement,
    escape_key,
    currency,
)


def product(url: str, conf) -> dict:
    b = get_webdriver(conf)
    b.get(url)

    data = {}

    data["title"] = b.find_element(
        By.XPATH, '//div[@data-test="mms-select-details-header"]/h1'
    ).text

    product_info_elements = b.find_elements(
        By.XPATH,
        '//div[@data-test="mms-select-details-header"]//p[@font-family="default"]',
    )
    ratings = re.findall(r"[-+]?\d*\.\d+|\d+", product_info_elements[0].text)
    data["rating"] = ratings[0]
    data["amount_of_ratings"] = ratings[1]

    data["product_number"] = product_info_elements[1].text.replace("Art.-Nr. ", "")

    try:
        data["discount"] = b.find_element(
            By.XPATH,
            '//div[@data-test="mms-product-price"]//div[@data-test="mms-badge"]/span',
        ).text
        orig_price = b.find_element(
            By.XPATH,
            '//div[@data-test="mms-product-price"]//div[@data-test="mms-badge"]/../p[1]/span[3]',
        ).text
        orig_price = orig_price[1:] + orig_price[:1]
        data["original_price"] = currency(orig_price)
    except exceptions.NoSuchElementException:
        pass

    price = b.find_element(
        By.XPATH, '//span[@data-test="branded-price-whole-value"]'
    ).text[:-1]
    price = price[2:] + price[:2]
    data["price"] = currency(price.strip())

    try:
        price_decimal = b.find_element(
            By.XPATH, '//span[@data-test="branded-price-decimal-value"]'
        ).text
        decimal = 0.0 if price_decimal == "–" else float(f"0.{price_decimal}")
        data["price"]["value"] += decimal
    except exceptions.NoSuchElementException:
        pass

    data["information"] = {}
    features_html = b.find_elements(
        By.XPATH, '//div[@data-test="pdp-features-content"]/div/div/table'
    )
    scrollToElement(b, features_html[0])
    for feature in features_html:
        title = escape_key(feature.find_element(By.XPATH, "./thead//p").text)
        data["information"][title] = {}
        scrollToElement(b, feature)
        for info in feature.find_elements(By.XPATH, "./tbody/tr"):
            scrollToElement(b, info)
            info_html = info.find_elements(By.XPATH, "./td/p")
            key = escape_key(info_html[0].text)
            val = info_html[1].text
            data["information"][title][key] = val

    b.quit()
    return data
