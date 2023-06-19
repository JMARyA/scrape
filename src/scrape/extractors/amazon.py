from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from ..val import currency, Language, printinfo, get_webdriver


def amazon_product(url: str, conf) -> dict:
    lang = conf.lang
    b = get_webdriver(conf)

    url = urlparse(url)
    query_params = dict(parse_qsl(url.query))
    query_params["language"] = "en_GB"
    match lang:
        case Language.de_DE:
            query_params["language"] = "de_DE"
    query_string = urlencode(query_params)
    url = urlunparse(url._replace(query=query_string))

    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    b.find_element(By.XPATH, '//*[@id="sp-cc-accept"]').click()

    info["product_title"] = b.find_element(By.XPATH, '//*[@id="productTitle"]').text

    info["star_rating"] = float(
        b.find_element(
            By.XPATH,
            '//*[@class="reviewCountTextLinkedHistogram noUnderline"]/span[1]/a/span',
        ).text.replace(",", ".")
    )

    price_symbol = b.find_element(
        By.XPATH, '//*[@id="corePrice_feature_div"]//span[@class="a-price-symbol"]'
    ).text
    whole = (
        b.find_element(
            By.XPATH, '//*[@id="corePrice_feature_div"]//span[@class="a-price-whole"]'
        )
        .text.replace(".", "")
        .replace(",", "")
    )
    fraction = b.find_element(
        By.XPATH, '//*[@id="corePrice_feature_div"]//span[@class="a-price-fraction"]'
    ).text
    info["price"] = currency(f"{whole}.{fraction}{price_symbol}")

    tech_details = {}
    tech_details_html = b.find_element(
        By.XPATH, '//*[@id="productDetails_techSpec_section_1"]/tbody'
    )
    for detail in tech_details_html.find_elements(By.TAG_NAME, "tr"):
        key = detail.find_element(By.TAG_NAME, "th").text
        value = detail.find_element(By.TAG_NAME, "td").text
        tech_details[key] = value
    info["technical_details"] = tech_details

    b.quit()
    return info
