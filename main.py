from pipeline.scraper.crawlers import NNCrawler, NNEWSCrawler, NIANNCrawler
from pipeline.scraper.core_utils import ScrapingConfig
from config import CRAWLER_CONFIG

def main() -> None:
    config = ScrapingConfig()
    crawler = NIANNCrawler(config.load_config(CRAWLER_CONFIG))
    urls = crawler.find_urls()
    print(urls)
    return

if __name__ == "__main__":
    main()
