from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from ..val import (
    printinfo,
    get_webdriver,
    download_media_raw,
    parse_duration,
    escape_unsafe_characters,
    window,
)
from datetime import timedelta
import re


def torrent(url: str, conf) -> dict:
    b = get_webdriver(conf)
    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    info_table_html = b.find_element(By.XPATH, '//*[@id="td_props"]/tbody')
    for entry in info_table_html.find_elements(By.TAG_NAME, "tr")[:-1]:
        try:
            key_name = entry.find_element(By.XPATH, './td[@class="label"]/b').text
        except:
            continue
        content = entry.find_element(By.XPATH, "./td[2]").text
        match key_name:
            case "Name:":
                info["name"] = content
            case "Torrent file:":
                torrent_file_url = entry.find_element(
                    By.XPATH, "./td[2]/a[1]"
                ).get_attribute("href")
                if conf.download_media:
                    download_media_raw(torrent_file_url, content, conf)
            case "Magnet:":
                info["magnet_url"] = entry.find_element(
                    By.XPATH, "./td[2]/a[1]"
                ).get_attribute("href")
            case "Infohash:":
                info["infohash"] = content
            case "Size:":
                info["size"] = content
            case "Owner:":
                if content != "hidden" and content != "none (abandoned torrent)":
                    info["owner"] = content
                    level = entry.find_element(
                        By.XPATH, "./td[2]/span[1]/img[1]"
                    ).get_attribute("src")
                    info["owner_level"] = int(level.split("/")[-1][:-4])
            case "Main Languages:":
                languages_html = entry.find_elements(By.XPATH, "./td[2]/span")
                languages = []
                for lang in languages_html:
                    languages.append(lang.get_attribute("title"))
                info["main_languages"] = languages
            case "Subtitle Languages:":
                languages_html = entry.find_elements(By.XPATH, "./td[2]/span")
                languages = []
                for lang in languages_html:
                    languages.append(lang.get_attribute("title"))
                info["subtitle_languages"] = languages
            case "Hits / Downloads:":
                (info["hits_amount"], info["downloads_amount"]) = content.split(" / ")
            case "Seeders / Leechers:":
                (info["seeders_amount"], info["leechers_amount"]) = content.split(" / ")
            case "Added / Last Active:":
                (info["added_timestamp"], last_active_timestamp) = content.split(" / ")
                info["last_active_timestamp"] = (
                    last_active_timestamp
                    if last_active_timestamp != "No active seeders in DB"
                    else None
                )
            case "Rating:":
                info["rating"] = float(
                    entry.find_element(By.XPATH, './td[2]/span[@id="ratingbars"]')
                    .get_attribute("title")
                    .split(" ")[0]
                )
            case "Description:":
                info["description"] = content
            case "Category:":
                info["category"] = content
            case "Subtitles:":
                if content != "":
                    info["subtitles"] = content
            case "Length:":
                if content != "":
                    info["length"] = content
                    lenght_duration = parse_duration(content)
                    if lenght_duration is not None:
                        info["length_in_minutes"] = lenght_duration.seconds / 60
            case "Genre:":
                if content != "":
                    info["genre"] = content
            case "Codec:":
                if content != "":
                    info["codec"] = content
            case "Ripper Info:":
                if content != "":
                    info["ripper_info"] = content
            case "Banned:":
                info["banned"] = True if content == "yes" else False
            case "Immutable:":
                info["immutable"] = True if content == "yes" else False
            case "Visible:":
                info["visible"] = True if content == "yes" else False

    files = []
    files_info_html = b.find_elements(By.XPATH, '//*[@id="td_files"]/tbody/*')[1:]
    for entry in files_info_html:
        file_name = entry.find_element(By.XPATH, "./td[1]").text
        file_size = entry.find_element(By.XPATH, "./td[2]").text
        files.append({"file_name": file_name, "file_size": file_size})
    info["files"] = files

    attachments = {}
    attachment_html = b.find_element(
        By.XPATH, '//table[@id="td_attachments"]/tbody/tr[1]/td[1]'
    )
    for el in attachment_html.find_elements(By.XPATH, "./a/img"):
        attachment_title = el.get_attribute("title")
        attachments[attachment_title] = el.get_attribute("src")
        if conf.download_media:
            download_media_raw(
                img.get_attribute("src"),
                f"{escape_unsafe_characters(attachment_title)}.png",
                conf,
            )
    info["attachments"] = attachments

    comments = []
    comments_html = b.find_element(By.XPATH, '//*[@id="comments"]/tbody')

    for comment in window(comments_html.find_elements(By.TAG_NAME, "tr"), 2, 2):
        comment_user = comment[0].find_element(By.XPATH, "./th/b/i").text
        comment_ts = (
            comment[0]
            .find_element(By.XPATH, './th/span[@class="commentdate"]')
            .text[7:]
        )
        comment_content = (
            comment[1].find_element(By.XPATH, './td/span[@class="commenttext"]').text
        )
        comment_content_html = comment[1].find_elements(
            By.XPATH, './td/span[@class="commenttext"]/a'
        )
        for el in comment_content_html:
            match el.tag_name:
                case "a":
                    link = f'[{el.text}]({el.get_attribute("href")})'
                    comment_content = comment_content.replace(el.text, link)
        comments.append(
            {"user": comment_user, "timestamp": comment_ts, "content": comment_content}
        )
    info["comments"] = comments

    b.quit()
    return info
