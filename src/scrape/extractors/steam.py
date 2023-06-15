from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import locale
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from ..val import currency, Language


def steam_game(url: str, lang: Language) -> dict:
    b = webdriver.Chrome()

    url = urlparse(url)
    query_params = dict(parse_qsl(url.query))
    query_params["l"] = "english"
    match lang:
        case Language.de_DE:
            query_params["l"] = "german"
    query_string = urlencode(query_params)
    url = urlunparse(url._replace(query=query_string))

    b.get(url)

    if "agecheck" in b.current_url:
        year = Select(b.find_element(By.XPATH, '//*[@id="ageYear"]'))
        year.select_by_value("1900")

        b.find_element(By.XPATH, '//*[@id="view_product_page_btn"]').click()

        WebDriverWait(b, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="appHubAppName"]'))
        )

    game_name: str = b.find_element(By.XPATH, '//*[@id="appHubAppName"]').text

    game_description = b.find_element(
        By.XPATH, '//*[@class="game_description_snippet"]'
    ).text

    game_release = b.find_element(By.XPATH, '//*[@class="release_date"]/div[2]').text

    match lang:
        case Language.de_DE:
            locale.setlocale(locale.LC_TIME, "de_DE")
            game_release = datetime.strptime(game_release, "%d. %b. %Y").strftime(
                "%Y-%m-%d"
            )
        case Language.en_US:
            locale.setlocale(locale.LC_TIME, "en_US")
            game_release = datetime.strptime(game_release, "%d %b, %Y").strftime(
                "%Y-%m-%d"
            )

    game_developer = b.find_element(By.XPATH, '//*[@id="developers_list"]/a').text
    game_publisher = b.find_elements(By.XPATH, '//*[@class="dev_row"]/div[2]')[1].text

    game_price = None

    try:
        game_orig_price = b.find_elements(
            By.XPATH,
            '//*[@class="game_area_purchase_game_wrapper"]/div/div[2]/div/div[1]/div[2]/*[@class="discount_original_price"]',
        )[0].text
        game_discount_price = b.find_elements(
            By.XPATH,
            '//*[@class="game_area_purchase_game_wrapper"]/div/div[2]/div/div[1]/div[2]/*[@class="discount_final_price"]',
        )[0].text
        game_price = {
            "original_price": currency(game_orig_price),
            "discount_price": currency(game_discount_price),
        }
    except:
        game_price = currency(
            b.find_element(
                By.XPATH,
                '//*[@class="game_area_purchase_game_wrapper"]/div/div[2]/div/*[@class="game_purchase_price price"]',
            ).text
        )

    b.quit()
    return {
        "name": game_name,
        "description": game_description,
        "release": game_release,
        "developer": game_developer,
        "publisher": game_publisher,
        "price": game_price,
    }
