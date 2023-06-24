#!python3
import argparse
from scrape.extractors import scrape_site
from scrape.val import Language, printinfo


class ShowSitesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from scrape.extractors import SupportedSites
        from rich import print

        print("Supported sites:")
        for site, site_url in SupportedSites.__members__.items():
            print("-", f"[red]{site}", "[", f"[purple]{site_url.value}", "]")

        parser.exit()


class Config:
    save_ts: bool = False
    language: Language
    download_media: bool = False
    http_proxy: str = None
    embed_media: bool = False


def main():
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument(
        "--sites", action=ShowSitesAction, nargs=0, help="Show all supported sites"
    )
    parser.add_argument(
        "-t", action="store_true", default=False, help="Store timestamp when scraping"
    )
    parser.add_argument(
        "-d", action="store_true", default=False, help="Download any found media urls"
    )
    parser.add_argument(
        "--lang",
        choices=list(Language._member_names_),
        default="en_US",
        help="Desired language to scrape in",
    )
    parser.add_argument(
        "--http-proxy",
        default=None,
        help="HTTP Proxy",
    )
    parser.add_argument(
        "-e",
        "--embed-media",
        action="store_true",
        default=False,
        help="Embed media urls as data urls",
    )
    parser.add_argument("url", type=str, help="URL to scrape")

    args = parser.parse_args()

    conf = Config()

    if args.t:
        conf.save_ts = True

    if args.d:
        conf.download_media = True

    if args.http_proxy is not None:
        printinfo(f"Using HTTP Proxy '{args.http_proxy}'")
        conf.http_proxy = args.http_proxy

    conf.embed_media = args.embed_media

    conf.language = Language.__members__[args.lang]

    scrape_site(args.url, conf)


if __name__ == "__main__":
    main()
