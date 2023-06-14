from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime


def igdb_game(url: str) -> dict:
    b = webdriver.Chrome()
    b.get(url)

    WebDriverWait(b, 1000)

    game_name: str = b.find_element(
        By.XPATH, "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/h1"
    ).text

    genres_html = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/p[2]",
    )
    genres_html = genres_html.find_elements(By.TAG_NAME, "a")
    genres = []
    for i in genres_html:
        genres.append(i.text)

    platforms_html = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/p[3]",
    )
    platforms_txt = platforms_html.text[11:]
    platforms = []
    for platform in platforms_txt.split(", "):
        platforms.append(platform)

    game_url = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[4]/div/input",
    ).get_attribute("value")

    desc = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/div[1]",
    ).text

    date_string = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/h2/span/span[1]",
    ).text
    game_release = datetime.strptime(date_string, "%b %d, %Y")

    ratings = b.find_element(By.XPATH, '//*[@class="gamepage-gauge"]').find_elements(
        By.TAG_NAME, "text"
    )
    member_rating = int(ratings[0].text)
    critic_rating = int(ratings[2].text)

    time_to_beat_data = b.find_element(
        By.XPATH, '//*[@id="content-page"]/div[2]/aside/table/tbody'
    )
    time_to_beat = {}
    for row in time_to_beat_data.find_elements(By.TAG_NAME, "tr"):
        time_to_beat[row.find_element(By.TAG_NAME, "th").text[:-1]] = row.find_element(
            By.TAG_NAME, "td"
        ).text

    b.quit()
    return {
        "name": game_name[:-4],
        "genre": genres,
        "platforms": platforms,
        "url": game_url,
        "description": desc,
        "released": game_release.strftime("%Y-%m-%d"),
        "ratings": {"member": member_rating, "critic": critic_rating},
        "time_to_beat": time_to_beat,
    }
