from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from ..val import printinfo, get_webdriver, download_media_raw


def torrent(url: str, conf) -> dict:
    b = get_webdriver(conf)
    printinfo(f"Scraping '{url}'")
    b.get(url)

    info = {}

    info_table_html = b.find_element(By.XPATH, '//*[@id="td_props"]/tbody')
    for entry in info_table_html.find_elements(By.TAG_NAME, "tr")[:-1]:
        key_name = entry.find_element(By.XPATH, "./td[1]/b").text
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
                info["owner"] = content
            case "Main Languages:":
                # todo : implement
                pass
            case "Subtitle Languages:":
                # todo : implement
                pass
            case "Hits / Downloads:":
                # todo : implement
                pass
            case "Seeders / Leechers:":
                # todo : implement
                pass
            case "Added / Last Active:":
                # todo : implement
                pass
            case "Rating:":
                # todo : implement
                pass
            case "Description:":
                info["description"] = content
            case "Category:":
                info["category"] = content
            case "Subtitles:":
                # todo : implement
                pass
            case "Length:":
                # todo : implement
                pass
            case "Genre:":
                # todo : implement
                pass
            case "Codec:":
                # todo : implement
                pass
            case "Ripper Info:":
                # todo : implement
                pass
            case "Comment Handling:":
                # todo : implement
                pass
            case "Banned:":
                # todo : implement
                pass
            case "Immutable:":
                # todo : implement
                pass
            case "Visible:":
                # todo : implement
                pass
        print(f"'{key_name}' : '{content}'")

    files = []
    files_info_html = b.find_elements(By.XPATH, '//*[@id="td_files"]/tbody/*')[1:]
    for entry in files_info_html:
        file_name = entry.find_element(By.XPATH, "./td[1]").text
        file_size = entry.find_element(By.XPATH, "./td[2]").text
        files.append({"file_name": file_name, "file_size": file_size})
    info["files"] = files

    # todo : implement

    b.quit()
    return info
