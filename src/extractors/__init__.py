from urllib.parse import urlparse
import extractors.igdb
import json
from rich import print

def scrape_site(url: str):
    _url = urlparse(url)
    host = _url.hostname

    match host:
        case "www.igdb.com":
            data = igdb.igdb_game(url)
            print(data)
        case _:
            print("[red]Error:", "Unknown site")