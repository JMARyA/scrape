from enum import Enum
import sys
from rich import print
from urllib.parse import urlparse
import requests
from seleniumwire import webdriver


def printinfo(s: str):
    print(f"[bold blue]Info:", s, file=sys.stderr)


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
    return webdriver.Chrome(seleniumwire_options=options)


def download_media(url: str, file_name: str, conf):
    file_ending = urlparse(url).path.split(".")[-1]
    file_name = f"{file_name}.{file_ending}"
    download_media_raw(url, file_name, conf)


def download_media_raw(url: str, file_name: str, conf):
    proxy = {}
    if conf.http_proxy is not None:
        proxy["http"] = conf.http_proxy

    response = requests.get(url, proxies=proxy)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
            printinfo(f"Saved '{url}' to '{file_name}'")
    else:
        printerr(f"Saving '{url}' to '{file_name}' failed")


def splitat(s: str, p: str) -> (str, str):
    split_values = s.split(p, 1)
    lang, value = p.join(split_values[:-1]), split_values[-1]
    return (lang, value)


def currency(v: str) -> dict:
    return {"currency": v[-1:], "value": float(v[:-1].replace(",", "."))}


class Language(Enum):
    en_US = 1
    de_DE = 2
