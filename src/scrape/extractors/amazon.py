from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from ..val import currency, Language


def amazon_product(url: str, lang: Language) -> dict:
    b = webdriver.Chrome()

    url = urlparse(url)
    query_params = dict(parse_qsl(url.query))
    query_params["language"] = "en_GB"
    match lang:
        case Language.de_DE:
            query_params["language"] = "de_DE"
    query_string = urlencode(query_params)
    url = urlunparse(url._replace(query=query_string))

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

    price_html = b.find_element(
        By.XPATH, '//*[@id="corePrice_feature_div"]/div[1]/span[1]/span[2]'
    )

    match lang:
        case Language.en_US:
            price_symbol = price_html.find_element(By.XPATH, "./span[1]").text
        case Language.de_DE:
            price_symbol = price_html.find_element(By.XPATH, "./span[3]").text
    match lang:
        case Language.en_US:
            whole = price_html.find_element(By.XPATH, "./span[2]").text
        case Language.de_DE:
            whole = price_html.find_element(By.XPATH, "./span[1]").text
    match lang:
        case Language.en_US:
            fraction = price_html.find_element(By.XPATH, "./span[3]").text
        case Language.de_DE:
            fraction = price_html.find_element(By.XPATH, "./span[2]").text
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
