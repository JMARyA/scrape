from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import locale
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from ..val import currency, Language, printinfo, get_webdriver, handle_media_url


def split_header(element):
    header = element.find_element(By.XPATH, './/span[@class="header"]').text
    value = element.text.replace(header, "", 1).strip()
    return (header.replace(":", ""), value)


def anime_search(url: str, conf) -> dict:
    b = get_webdriver(conf)

    b.get(url)

    data = {}

    data["query"] = b.find_element(By.XPATH, '//*[@id="item-key-a-text"]').text.replace(
        'Title starts with "', ""
    )[:-1]
    data["results"] = []

    for result in b.find_elements(By.XPATH, '//ul[@class="covers"]/li'):
        link = result.find_element(By.XPATH, ".//a").get_attribute("href")
        data["results"].append(link)

    b.quit()
    return data


def anime(url: str, conf) -> dict:
    b = get_webdriver(conf)

    b.get(url)

    data = {}

    WebDriverWait(b, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@class="needsclick cmp-root-container"]')
        )
    )
    accept_cookies = b.execute_script(
        'return document.querySelector("#top > div.needsclick.cmp-root-container").shadowRoot.querySelector("#consentDialog > div.cmp_ui.cmp_ext_text.cmp_state-stacks > div.cmp_navi > div > div.cmp_mainButtons > div > div.cmp_primaryButtonLine > div > div")'
    )
    accept_cookies.click()

    anime_info_section = b.find_element(By.XPATH, '//section[@id="information"]')

    # Extract the title and cover image
    title_element = anime_info_section.find_element(
        By.XPATH, './/div[@class="title"]//strong[@class="f16"]'
    )
    data["original_title"] = anime_info_section.find_element(
        By.XPATH, './/div[@class="title"]//div'
    ).text
    data["title"] = title_element.text
    cover_image_url = anime_info_section.find_element(
        By.XPATH, './/figure[@id="cover-container"]/img'
    ).get_attribute("src")
    data["cover"] = handle_media_url(cover_image_url, "cover", False, conf)

    # Extract other details
    details = {}
    details_elements = anime_info_section.find_elements(
        By.XPATH, "./div/ul/li[2]/ul/li[1]/div"
    )
    for element in details_elements:
        if element.get_attribute("class") == "title":
            continue
        key, val = split_header(element)
        if element.get_attribute("class") == "creators":
            details[key] = val.split(", ")
            continue
        if element.get_attribute("class") == "websites":
            links = []
            links_html = element.find_elements(By.XPATH, "./a")
            for l in links_html:
                links.append(l.get_attribute("href"))
            details[key] = links
            continue

        details[key] = val

    data["details"] = details

    for desc in b.find_elements(By.XPATH, '//section[@id="description"]//button'):
        desc_lang = desc.get_attribute("lang")
        if desc.get_attribute("class") != "active":
            show_more_button = b.find_element(
                By.XPATH, f'//section[@id="description"]//button[@lang="{desc_lang}"]'
            )
            b.execute_script("arguments[0].scrollIntoView();", show_more_button)
            show_more_button.click()

    descriptions = {}
    for desc in b.find_elements(
        By.XPATH, '//section[@id="description"]//div[@class="textblock details-text"]'
    ):
        desc_lang = desc.get_attribute("lang")
        desc_text = desc.text
        descriptions[desc_lang] = desc_text
    data["description"] = descriptions

    tag_cloud = b.find_element(By.XPATH, '//*[@id="description"]//ul[@class="cloud"]')
    genres = {"main": [], "sub": []}
    tags = []
    for tag in tag_cloud.find_elements(By.XPATH, "./li/a"):
        if tag.get_attribute("class") == "gg showpop":
            genres["main"].append(tag.text)
        if tag.get_attribute("class") == "gc showpop":
            if tag.text != "":
                genres["sub"].append(tag.text)
        if tag.get_attribute("class") == "gt showpop":
            tags.append(tag.text)
    data["genres"] = genres
    data["tags"] = tags

    show_more_button = b.find_element(
        By.XPATH, '//*[@id="information"]/div/ul/li[2]/div/button'
    )
    b.execute_script("arguments[0].scrollIntoView();", show_more_button)
    show_more_button.click()

    lang_html = b.find_elements(By.XPATH, '//*[@id="information"]/div/ul/li[2]/ul/li')
    dubs = {}
    try:
        dubs[
            b.find_element(By.XPATH, '//div[@class="title"]').get_attribute("lang")
        ] = {}
    except:
        pass
    subs = {}
    for dub in lang_html:
        lang_info = dub.find_elements(By.XPATH, "./div")
        if len(lang_info) != 4:
            continue

        lang_lang = lang_info[0].get_attribute("lang")
        is_dub = False
        try:
            is_dub_html = lang_info[0].find_element(
                By.XPATH, './/span[@class="speaker"]'
            )
            is_dub = True
        except:
            pass

        lang_status = split_header(lang_info[1])
        lang_release = split_header(lang_info[2])
        lang_publisher = split_header(lang_info[3])
        if is_dub:
            dubs[lang_lang] = {}
            dubs[lang_lang][lang_status[0]] = lang_status[1]
            dubs[lang_lang][lang_release[0]] = lang_release[1]
            dubs[lang_lang][lang_publisher[0]] = lang_publisher[1]
        else:
            subs[lang_lang] = {}
            subs[lang_lang][lang_status[0]] = lang_status[1]
            subs[lang_lang][lang_release[0]] = lang_release[1]
            subs[lang_lang][lang_publisher[0]] = lang_publisher[1]

    data["dubs"] = dubs
    data["subs"] = subs

    b.quit()
    return data
