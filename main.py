from config import CRAWLER_CONFIG
from pipeline.scraper.core_utils import ScrapingConfig
from pipeline.scraper.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraper.parsers import NNPasrser, NIANNParser, NNEWSParser

def main() -> None:
    config = ScrapingConfig()
    crawler = NNEWSCrawler(config.load_config(CRAWLER_CONFIG))
    urls = crawler.find_urls()
    for url in urls:
        parser = NNEWSParser(url, config.load_config(CRAWLER_CONFIG))
        print(parser.parse_raw_text())
    print(urls)
    return

if __name__ == "__main__":
    main()
