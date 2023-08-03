from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from datetime import datetime
import locale
import json
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from ..val import (
    currency,
    Language,
    printinfo,
    printwarn,
    get_webdriver,
    handle_media_url,
    scrollToElement,
    escape_key,
    parse_duration,
)
from urllib.parse import quote


def parse_date(dt_str):
    return datetime.strptime(dt_str, "%B %d, %Y").strftime("%Y-%m-%d")


def tv(url: str, conf) -> dict:
    b = get_webdriver(conf)

    # TODO : Handle language
    lang_cookie = {
        "name": "tmdb.prefs",
        "value": quote(
            json.dumps(
                {
                    "i18n_fallback_language": "en-US",
                    "locale": "en-US",
                    "country_code": "US",
                }
            )
        ),
        "domain": "www.themoviedb.org",
        "path": "/",
        "expires": None,
        "secure": True,
        "httpOnly": True,
    }
    b.get("https://www.themoviedb.org")
    b.delete_cookie("tmdb.prefs")
    b.add_cookie(lang_cookie)

    b.get(url)

    data = {}

    try:
        error_page = b.find_element(
            By.XPATH, '//*[@id="main"]//div[@class="error_wrapper"]'
        )
        data = {"error": "page unavailable"}
        b.quit()
        return data
    except:
        pass

    data["title"] = b.find_element(
        By.XPATH, '//*[@id="original_header"]//div[@class="title ott_true"]/h2/a'
    ).text
    data["release_year"] = b.find_element(
        By.XPATH, '//*[@id="original_header"]//div[@class="title ott_true"]/h2/span'
    ).text[1:][:-1]

    rating_html = b.find_element(
        By.XPATH, '//div[@class="user_score_chart"]/div[1]/span'
    ).get_attribute("class")
    (_, rating) = rating_html.split("icon-r", 2)
    data["user_rating"] = int(rating)

    try:
        data["age_certification"] = b.find_element(
            By.XPATH, '//*[@id="original_header"]//span[@class="certification"]'
        ).text
    except:
        pass

    genres_html = b.find_elements(
        By.XPATH, '//*[@id="original_header"]//span[@class="genres"]/a'
    )
    data["genres"] = list(
        map(
            lambda x: x.text,
            genres_html,
        )
    )

    data["overview"] = b.find_element(
        By.XPATH, '//*[@id="original_header"]//div[@class="overview"]'
    ).text

    cover_url = b.find_element(
        By.XPATH, '//*[@id="original_header"]//div[@class="poster"]//img'
    ).get_attribute("src")
    data["cover"] = handle_media_url(cover_url, "cover", False, conf)

    facts_html = b.find_elements(
        By.XPATH, '//*[@id="media_v4"]//section[@class="facts left_column"]/p'
    )
    for fact in facts_html:
        try:
            key = fact.find_element(By.XPATH, "./strong").text
            if key == "Networks":
                continue
            data[escape_key(key)] = fact.text.replace(f"{key}\n", "")
        except:
            pass

    tags = []
    tags_html = b.find_elements(
        By.XPATH,
        '//*[@id="media_v4"]//section[@class="keywords right_column"]/ul[1]/li',
    )
    for tag in tags_html:
        tags.append(tag.find_element(By.XPATH, "./a").text)
    data["tags"] = tags

    # seasons & episodes
    all_seasons_url = b.find_element(
        By.XPATH, '//*[@id="media_v4"]//section[@class="panel season"]/p[1]/a'
    ).get_attribute("href")
    b.get(all_seasons_url)

    seasons = []
    seasons_urls = list(
        map(
            lambda x: x.get_attribute("href"),
            b.find_elements(
                By.XPATH,
                '//*[@id="media_v4"]//div[@class="season_wrapper"]/section/div/a',
            ),
        )
    )

    for season in seasons_urls:
        season_data = season_page(season, conf, b)
        seasons.append(season_data)

    data["seasons"] = seasons

    b.quit()
    return data


def season_page(url, conf, b):
    b.get(url)

    season = {}
    season["season_number"] = int(url.split("/")[-1])
    season["title"] = b.find_element(
        By.XPATH, '//*[@id="main"]//div[@class="title ott_true"]//a'
    ).text
    try:
        season["release_year"] = int(
            b.find_element(
                By.XPATH, '//*[@id="main"]//div[@class="title ott_true"]//span'
            ).text[1:][:-1]
        )
    except:
        pass

    season["amount_of_episodes"] = int(
        b.find_element(
            By.XPATH, '//*[@id="main_column"]//h3[@class="episode_sort space"]/span'
        ).text
    )

    episodes = []
    episodes_html = b.find_element(
        By.XPATH, '//*[@id="main_column"]//div[@class="episode_list"]'
    )
    for e in episodes_html.find_elements(By.XPATH, './div[@class="card"]'):
        episode = {}
        episode["episode_number"] = int(
            e.find_element(By.XPATH, './/span[@class="episode_number"]').text
        )
        episode["title"] = e.find_element(
            By.XPATH, './/div[@class="episode_title"]//a'
        ).text
        episode["rating"] = float(
            e.find_element(
                By.XPATH, './/div[@class="episode_title"]/div[1]/div[1]/div[1]'
            ).text
        )
        episode["release_date"] = parse_date(
            e.find_element(
                By.XPATH,
                './/div[@class="episode_title"]//div[@class="date"]/span[@class="date"]',
            ).text
        )
        try:
            episode["runtime_in_minutes"] = (
                parse_duration(
                    e.find_element(
                        By.XPATH,
                        './/div[@class="episode_title"]//div[@class="date"]/span[@class="runtime"]',
                    ).text
                ).seconds
                / 60
            )
        except exceptions.NoSuchElementException:
            pass

        episode["overview"] = e.find_element(
            By.XPATH, './/div[@class="info"]//div[@class="overview"]/p'
        ).text
        episodes.append(episode)

    season["episodes"] = episodes

    return season
