#!python3
import argparse
from scrape.extractors import scrape_site


class ShowSitesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from scrape.extractors import supported_sites
        from rich import print

        print("Supported sites:")
        for site, site_url in supported_sites.__members__.items():
            print(f"-", f"[red]{site}", "[", f"[purple]{site_url.value}", "]")

        parser.exit()


def main():
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument(
        "--sites", action=ShowSitesAction, nargs=0, help="Show all supported sites"
    )
    parser.add_argument("url", type=str, help="URL to scrape")

    args = parser.parse_args()

    scrape_site(args.url)


if __name__ == "__main__":
    main()
