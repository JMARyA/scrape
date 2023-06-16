from urllib.parse import urlparse
import json
from rich import print
import sys
from . import igdb, steam, aur, amazon
from ..val import Language, printerr, printwarn
from enum import Enum
import datetime
import pytz


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


def language_ignored_warn(conf):
    if conf.language != Language.en_US:
        printwarn("Language setting is not used by this extractor")


def scrape_site(url: str, conf):
    _url = urlparse(url)
    host = _url.hostname

    ts = datetime.datetime.now(pytz.utc)

    match host:
        case supported_sites.IGDB.value:
            language_ignored_warn(conf)
            data = igdb.igdb_game(url)
        case supported_sites.STEAM.value:
            data = steam.steam_game(url, conf.language)
        case supported_sites.AUR.value:
            language_ignored_warn(conf)
            data = aur.aur_package(url)
        case supported_sites.AMAZON.value:
            data = amazon.amazon_product(url, conf.language)
        case _:
            printerr("Unknown site")
            exit(1)

    if conf.save_ts:
        data["scraped_at"] = ts.strftime("%Y-%m-%d %H:%M:%S %z")

    present(data)
