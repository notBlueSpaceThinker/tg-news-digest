from config import SCRAPING_CONFIG
from pipeline.preprocessing.preprocessing import (clean, lemmatize,
                                                  remove_stop_words,
                                                  word_tokenize)
from pipeline.scraping.core_utils import ScrapingConfig
from pipeline.scraping.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraping.parsers import NIANNParser, NNEWSParser, NNPasrser
from utils import io

io.ensure_data_paths()

def run_scraping_pipeline() -> None:
    config = ScrapingConfig().load_config(SCRAPING_CONFIG)
    crawlers = {
        "NIANN": NIANNCrawler(config),
        "NN": NNCrawler(config),
        "NNEWS": NNEWSCrawler(config)
    }
    parsers = {
        "NIANN": NIANNParser,
        "NN": NNPasrser,
        "NNEWS": NNEWSParser
    }
    for portal_name, crawler in crawlers.items():
        urls = crawler.find_urls()
        for url in urls:
            parser = parsers[portal_name](url, config)

            io.save_to_raw(url, parser.parse_raw_text())
            io.save_to_meta(url, parser.parse_meta_data())


def run_preprocessing_pipeline() -> None:
    for hashed_url, text in io.get_raw_texts():
        cleaned_text = clean(text)
        removed_stop_words = remove_stop_words(word_tokenize(cleaned_text))
        if isinstance(removed_stop_words, str):
            removed_stop_words = word_tokenize(removed_stop_words)
        lemmatized_text = lemmatize(removed_stop_words, concat=True)

        io.save_to_cleaned(hashed_url, cleaned_text)
        io.save_to_lemmatized(hashed_url, str(lemmatized_text))


def run_inference_pipeline() -> None:
    pass


def run_analytics_pipeline() -> None:
    pass


def run_full_pipeline() -> None:
    run_scraping_pipeline()
    run_preprocessing_pipeline()
    run_inference_pipeline()
    run_analytics_pipeline()