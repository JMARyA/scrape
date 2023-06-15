from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from ..val import splitat


def igdb_game(url: str) -> dict:
    b = webdriver.Chrome()
    b.get(url)

    WebDriverWait(b, 1000)

    info = {}

    info["name"] = b.find_element(
        By.XPATH, '//*[@class="gamepage-title-wrapper"]/h1'
    ).text[:-4]

    info["cover"] = b.find_element(
        By.XPATH, '//*[@class="gamepage-cover"]/img[1]'
    ).get_attribute("src")

    genre_and_platform_htmls = b.find_elements(
        By.XPATH, '//*[@class="gamepage-tabs"]/div[2]/p/span[@class="text-semibold"]/..'
    )

    genres_html = genre_and_platform_htmls[0]
    genres_html = genres_html.find_elements(By.TAG_NAME, "a")
    genres = []
    for i in genres_html:
        genres.append(i.text)
    info["genre"] = genres

    platforms_html = genre_and_platform_htmls[1]
    platforms_txt = platforms_html.text[11:]
    platforms = []
    for platform in platforms_txt.split(", "):
        platforms.append(platform)
    info["platforms"] = platforms

    info["url"] = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[4]/div/input",
    ).get_attribute("value")

    info["description"] = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/div[1]",
    ).text

    date_string = b.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/h2/span/span[1]",
    ).text
    info["release"] = datetime.strptime(date_string, "%b %d, %Y")

    releases = []
    releases_html = b.find_element(
        By.XPATH, '//*[@class="optimisly-game-maininfo"]/div[2]'
    )
    for release in releases_html.find_elements(By.XPATH, "./*"):
        release_platform = release.find_element(By.XPATH, "./div[1]/span").text
        release_info_html = release.find_element(
            By.XPATH, "./div[2]/div[1]/div[1]/span"
        )
        release_date = release_info_html.find_element(By.TAG_NAME, "time").text
        release_info = release_info_html.find_element(By.TAG_NAME, "strong").text
        releases.append(
            {"platform": release_platform, "date": release_date, "info": release_info}
        )
    info["releases"] = releases

    developers = []
    developers_html = b.find_element(
        By.XPATH, '//*[@class="optimisly-game-maininfo"]/div[@itemprop="author"]/span'
    )
    for dev in developers_html.find_elements(By.TAG_NAME, "a"):
        developers.append(dev.text)
    info["developers"] = developers

    publishers = []
    pub_html = b.find_element(
        By.XPATH,
        '//*[@class="optimisly-game-maininfo"]/span[@itemprop="publisher"]/span',
    )
    for pub in pub_html.find_elements(By.TAG_NAME, "a"):
        publishers.append(pub.text)
    info["publishers"] = publishers

    ratings = b.find_element(By.XPATH, '//*[@class="gamepage-gauge"]').find_elements(
        By.TAG_NAME, "text"
    )
    member_rating = int(ratings[0].text)
    critic_rating = int(ratings[2].text)
    info["ratings"] = ({"member": member_rating, "critic": critic_rating},)

    time_to_beat_data = b.find_element(
        By.XPATH, '//*[@id="content-page"]/div[2]/aside/table/tbody'
    )
    time_to_beat = {}
    for row in time_to_beat_data.find_elements(By.TAG_NAME, "tr"):
        time_to_beat[row.find_element(By.TAG_NAME, "th").text[:-1]] = row.find_element(
            By.TAG_NAME, "td"
        ).text
    info["time_to_beat"] = time_to_beat

    b.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    b.find_element(
        By.XPATH,
        '//*[@id="game-storyline"]/span[@class="text-purple cursor-pointer charLimitMore"]',
    ).click()
    info["storyline"] = b.find_element(By.XPATH, '//*[@id="game-storyline"]/p').text

    recommend_div = b.find_element(
        By.XPATH, '//*[@id="content-page"]/div[2]/div[2]/ul/div[2]/div'
    )
    recommended = []
    for game in recommend_div.find_elements(By.TAG_NAME, "li"):
        game_link = game.find_element(By.TAG_NAME, "a").get_attribute("href")
        recommended.append(game_link)
    info["recommendations"] = recommended

    b.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    b.find_element(By.XPATH, '//*[@class="language-supports-display"]/button').click()
    for el in b.find_elements(
        By.XPATH,
        '//*[@class="optimisly-game-extrainfo2"]/div/div/span[@class="text-purple cursor-pointer"]',
    ):
        el.click()
    extra_info = ""
    extra_info_html = b.find_element(
        By.XPATH, '//*[@class="optimisly-game-extrainfo2"]'
    )
    for el in extra_info_html.find_elements(By.XPATH, "./*"):
        extra_info += el.text + "\n"

    extra_map = {}
    last = ""
    for line in extra_info.split("\n"):
        line = line.strip()

        if line == "":
            continue

        if line.endswith(":"):
            last = line[:-1]
            extra_map[last] = []
        else:
            extra_map[last].append(line)

    for key in extra_map.keys():
        if key == "Localized titles":
            titles = extra_map[key]
            title_map = {}
            for title in titles:
                lang, value = splitat(title, ": ")
                title_map[lang] = value
            extra_map[key] = title_map
        if key == "Alternative titles":
            titles = extra_map[key]
            title_map = {}
            for title in titles:
                lang, value = splitat(title, ": ")
                title_map[lang] = value
            extra_map[key] = title_map
        if key == "Keywords":
            keywords = extra_map[key][0]
            extra_map[key] = keywords.split(", ")
        if key == "Supported Languages":
            items = extra_map[key]
            support_langs = {"audio": [], "subtitles": [], "interface": []}
            for item in items:
                if item == "Audio Subtitles Interface":
                    continue
                if item == "Hide":
                    continue

                lang, support = splitat(item, ": ")
                support = support.split(" ")

                match len(support):
                    case 2:
                        support_langs["interface"].append(lang)
                        support_langs["subtitles"].append(lang)
                    case 3:
                        support_langs["interface"].append(lang)
                        support_langs["subtitles"].append(lang)
                        support_langs["audio"].append(lang)
            extra_map[key] = support_langs

    info.update(extra_map)

    b.quit()
    return info
