from config import CRAWLER_CONFIG
from pipeline.scraper.core_utils import ScrapingConfig
from pipeline.scraper.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraper.parsers import NNPasrser, NIANNParser, NNEWSParser
from utils import io

def main() -> None:
    io.ensure_data_paths()
    config = ScrapingConfig()
    crawler = NIANNCrawler(config.load_config(CRAWLER_CONFIG))
    urls = crawler.find_urls()
    for url in urls:
        parser = NIANNParser(url, config.load_config(CRAWLER_CONFIG))
        io.save_url_to_hash(url)
        io.save_to_raw(url, parser.parse_raw_text())
    print(urls)
    return
    pass

if __name__ == "__main__":
    main()
