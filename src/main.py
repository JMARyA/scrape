#!python3
import argparse
from scrape.extractors import scrape_site
from scrape.val import Language


class ShowSitesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from scrape.extractors import supported_sites
        from rich import print

        print("Supported sites:")
        for site, site_url in supported_sites.__members__.items():
            print(f"-", f"[red]{site}", "[", f"[purple]{site_url.value}", "]")

        parser.exit()


class Config:
    save_ts: bool = False
    language: Language


def main():
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument(
        "--sites", action=ShowSitesAction, nargs=0, help="Show all supported sites"
    )
    parser.add_argument("-t", action="store_true", help="Store timestamp when scraping")
    parser.add_argument(
        "--lang",
        choices=list(Language._member_names_),
        default="en_US",
        help="Desired language to scrape in",
    )
    parser.add_argument("url", type=str, help="URL to scrape")

    args = parser.parse_args()

    conf = Config()

    if args.t:
        conf.save_ts = True

    conf.language = Language.__members__[args.lang]

    scrape_site(args.url, conf)


if __name__ == "__main__":
    main()
