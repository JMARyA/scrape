from urllib.parse import urlparse
import json
from rich import print
import sys
from . import igdb, steam, aur, amazon, postman
from ..val import Language, printerr, printwarn
from enum import Enum
import datetime
import pytz


def present(data: dict):
    """
    Prints the data dictionary in a human-readable format if stdout is a terminal,
    otherwise writes the data as a JSON string to stdout.

    Args:
        data (dict): The data dictionary to be presented.
    """
    if sys.stdout.isatty():
        print(data)
    else:
        sys.stdout.write(json.dumps(data, ensure_ascii=False))


class SupportedSites(Enum):
    """
    Enum class representing supported sites for web scraping.
    """

    IGDB = "www.igdb.com"
    STEAM = "store.steampowered.com"
    AUR = "aur.archlinux.org"
    AMAZON = "www.amazon.de"
    POSTMAN = "tracker2.postman.i2p"


def language_ignored_warn(conf):
    if conf.language != Language.en_US:
        printwarn("Language setting is not used by this extractor")


def scrape_site(url: str, conf):
    _url = urlparse(url)
    host = _url.hostname

    ts = datetime.datetime.now(pytz.utc)

    match host:
        case SupportedSites.IGDB.value:
            language_ignored_warn(conf)
            data = igdb.igdb_game(url, conf)
        case SupportedSites.STEAM.value:
            data = steam.steam_game(url, conf)
        case SupportedSites.AUR.value:
            language_ignored_warn(conf)
            data = aur.aur_package(url, conf)
        case SupportedSites.AMAZON.value:
            data = amazon.amazon_product(url, conf)
        case SupportedSites.POSTMAN.value:
            language_ignored_warn(conf)
            data = postman.torrent(url, conf)
        case _:
            printerr("Unknown site")
            exit(1)

    if conf.save_ts:
        data["scraped_at"] = ts.strftime("%Y-%m-%d %H:%M:%S %z")

    present(data)
