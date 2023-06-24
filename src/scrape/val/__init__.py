from enum import Enum
import sys
from rich import print
from urllib.parse import urlparse
import requests
from seleniumwire import webdriver
from selenium import webdriver as swd
from datetime import timedelta, datetime
import re
from typing import List
import base64
import magic


def window(lst: List[int], size: int, stride: int) -> List[List[int]]:
    if size <= 0 or stride <= 0:
        raise ValueError("Window size and stride must be greater than zero.")
    if size > len(lst):
        raise ValueError("Window size cannot exceed the list length.")

    return [lst[i : i + size] for i in range(0, len(lst), stride)]


def printinfo(s: str):
    print("[bold blue]Info:", s, file=sys.stderr)


def printerr(s: str):
    print("[red]:x: Error:", s, file=sys.stderr)


def printwarn(s: str):
    print("[bold yellow]:warning: Warning:", s, file=sys.stderr)


def get_webdriver(conf):
    options = {
        "proxy": {
            "http": conf.http_proxy,
            "no_proxy": "localhost,127.0.0.1",
        }
    }
    if conf.http_proxy is not None:
        return webdriver.Chrome(seleniumwire_options=options)
    else:
        return swd.Chrome()


def escape_unsafe_characters(filename):
    unsafe_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'
    return re.sub(unsafe_chars, "_", filename)


def handle_media_url(url: str, file_name: str, raw_file_name: bool, conf):
    if conf.download_media or conf.embed_media:
        data = donwload(url, conf)
        if data is None:
            printerr(f"Saving '{url}' to '{file_name}' failed")
            return url
        if conf.download_media:
            if raw_file_name:
                save_raw(url, data, file_name)
            else:
                save(url, file_name, data)
        if conf.embed_media:
            return to_data_url(data)
    return url


def to_data_url(file_data):
    base64_data = base64.b64encode(file_data).decode("utf-8")

    mime_type = magic.from_buffer(file_data, mime=True)
    if mime_type is None:
        mime_type = "application/octet-stream"

    return "data:{};base64,{}".format(mime_type, base64_data)


def donwload(url: str, conf):
    proxy = {}
    if conf.http_proxy is not None:
        proxy["http"] = conf.http_proxy

    response = requests.get(url, proxies=proxy)
    if response.status_code == 200:
        return response.content
    else:
        return None


def save_raw(url: str, data, file_name: str):
    with open(file_name, "wb") as file:
        file.write(data)
        printinfo(f"Saved '{url}' to '{file_name}'")


def save(url: str, file_name: str, data):
    file_ending = urlparse(url).path.split(".")[-1]
    file_name = f"{file_name}.{file_ending}"
    save_raw(url, data, file_name)


def splitat(s: str, p: str) -> (str, str):
    split_values = s.split(p, 1)
    lang, value = p.join(split_values[:-1]), split_values[-1]
    return (lang, value)


def parse_duration(s: str) -> timedelta:
    try:
        # format: "? h ? min"
        hours = int(re.search(r"(\d+)\s*h", s).group(1))
        minutes = int(re.search(r"(\d+)\s*min", s).group(1))
        return timedelta(hours=hours, minutes=minutes)
    except:
        pass

    try:
        # format: "??:??:??"
        hours = int(s.split(":")[0])
        minutes = int(s.split(":")[1])
        seconds = int(s.split(":")[2])
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except:
        pass

    try:
        # format : "??:??:??.??"
        time_duration = datetime.strptime(s, "%H:%M:%S.%f").time()
        return timedelta(
            hours=time_duration.hour,
            minutes=time_duration.minute,
            seconds=time_duration.second,
            microseconds=time_duration.microsecond,
        )
    except:
        pass

    # no valid format found
    return None


def currency(v: str) -> dict:
    return {"currency": v[-1:], "value": float(v[:-1].replace(",", "."))}


class Language(Enum):
    en_US = 1
    de_DE = 2
