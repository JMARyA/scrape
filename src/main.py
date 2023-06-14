import sys
from extractors import scrape_site

def main():
    url = sys.argv[1]
    scrape_site(url)

if __name__ == "__main__":
    main()