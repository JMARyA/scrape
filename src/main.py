import argparse
from scrape.extractors import scrape_site


def main():
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument("url", type=str, help="URL to scrape")

    args = parser.parse_args()

    scrape_site(args.url)


if __name__ == "__main__":
    main()
