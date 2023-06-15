from urllib.parse import urlparse
import json
from rich import print
import sys
from . import igdb, steam, aur, amazon
from ..val import Language
from enum import Enum


def present(data: dict):
    if sys.stdout.isatty():
        print(data)
    else:
        sys.stdout.write(json.dumps(data, ensure_ascii=False))


class supported_sites(Enum):
    IGDB = "www.igdb.com"
    STEAM = "store.steampowered.com"
    AUR = "aur.archlinux.org"
    AMAZON = "www.amazon.de"


def scrape_site(url: str):
    _url = urlparse(url)
    host = _url.hostname

    match host:
        case supported_sites.IGDB:
            data = igdb.igdb_game(url)
            present(data)
        case supported_sites.STEAM:
            data = steam.steam_game(url, Language.en_US)
            present(data)
        case supported_sites.AUR:
            data = aur.aur_package(url)
            present(data)
        case supported_sites.AMAZON:
            data = amazon.amazon_product(url, Language.en_US)
            present(data)
        case _:
            print("[red]Error:", "Unknown site")
