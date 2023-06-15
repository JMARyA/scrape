from urllib.parse import urlparse
import json
from rich import print
import sys
from . import igdb, steam, aur
from ..val import Language


def present(data: dict):
    if sys.stdout.isatty():
        print(data)
    else:
        sys.stdout.write(json.dumps(data, ensure_ascii=False))


def scrape_site(url: str):
    _url = urlparse(url)
    host = _url.hostname

    match host:
        case "www.igdb.com":
            data = igdb.igdb_game(url)
            present(data)
        case "store.steampowered.com":
            data = steam.steam_game(url, Language.en_US)
            present(data)
        case "aur.archlinux.org":
            data = aur.aur_package(url)
            present(data)
        case _:
            print("[red]Error:", "Unknown site")
