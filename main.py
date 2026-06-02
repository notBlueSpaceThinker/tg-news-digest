from config import CRAWLER_CONFIG
from pipeline.scraper.core_utils import ScrapingConfig
from pipeline.scraper.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraper.parsers import NIANNParser, NNEWSParser, NNPasrser
from pipeline.text_processing.processing import clean, remove_stop_words, lemmatize
from utils import io


def main() -> None:
    io.ensure_data_paths()
    config = ScrapingConfig()
    crawler = NNCrawler(config.load_config(CRAWLER_CONFIG))
    urls = crawler.find_urls()
    for url in urls:
        parser = NNPasrser(url, config.load_config(CRAWLER_CONFIG))
        io.save_url_to_hash(url)
        text = parser.parse_raw_text()
        io.save_to_raw(url, text)
        print(clean_text(text))
        print(remove_stop_words(clean_text(text)))
    return
    # pass

if __name__ == "__main__":
    main()
