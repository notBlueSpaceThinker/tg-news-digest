from config import SCRAPING_CONFIG
from pipeline.inference.inference import run_ner, run_zero_shot
from pipeline.preprocessing.preprocessing import (clean, lemmatize,
                                                  remove_stop_words,
                                                  word_tokenize)
from pipeline.scraping.core_utils import ScrapingConfig
from pipeline.scraping.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraping.parsers import NIANNParser, NNEWSParser, NNParser
from utils import io

io.ensure_data_paths()

def run_scraping_pipeline() -> None:
    """
    Execute the web scraping pipeline.
    """
    config = ScrapingConfig().load_config(SCRAPING_CONFIG)
    crawlers = {
        "NIANN": NIANNCrawler(config),
        "NN": NNCrawler(config),
        "NNEWS": NNEWSCrawler(config)
    }
    parsers = {
        "NIANN": NIANNParser,
        "NN": NNParser,
        "NNEWS": NNEWSParser
    }
    for portal_name, crawler in crawlers.items():
        urls = crawler.find_urls()
        raw_handler = io.TextFileHandler("raw")
        meta_handler = io.JsonFileHandler("meta")
        for url in urls:
            parser = parsers[portal_name](url, config)

            raw_handler.save(url, parser.parse_raw_text())
            meta_handler.save(url, parser.parse_meta_data())


def run_preprocessing_pipeline() -> None:
    """
    Execute the text preprocessing pipeline.
    """
    raw_handler = io.TextFileHandler("raw")
    cleaned_handler = io.TextFileHandler("cleaned")
    lemmatized_handler = io.TextFileHandler("lemmatized")
    for hashed_url, text in raw_handler.yield_all():
        cleaned_text = clean(text)
        removed_stop_words = remove_stop_words(word_tokenize(cleaned_text))
        if isinstance(removed_stop_words, str):
            removed_stop_words = word_tokenize(removed_stop_words)
        lemmatized_text = lemmatize(removed_stop_words, concat=True)

        cleaned_handler.save(hashed_url, cleaned_text)
        lemmatized_handler.save(hashed_url, str(lemmatized_text))


def run_inference_pipeline() -> None:
    """
    Execute model inference pipeline.
    """
    cleaned_handler = io.TextFileHandler("cleaned")
    zero_shot_handler = io.JsonFileHandler("zero-shot")
    for hashed_url, text in cleaned_handler.yield_all():
        zero_shot = run_zero_shot(text)
        zero_shot_handler.save(hashed_url, zero_shot)

    raw_handler = io.TextFileHandler("raw")
    ner_handler = io.JsonFileHandler("ner")
    for hashed_url, text in raw_handler.yield_all():
        ner = run_ner(text)
        ner_handler.save(hashed_url, ner)


def run_analytics_pipeline() -> None:
    """
    Generate corpus statistics and save visualization reports.
    """
    pass


def run_full_pipeline() -> None:
    """
    Orchestrate all the pipelines and run them.
    """
    run_scraping_pipeline()
    run_preprocessing_pipeline()
    run_inference_pipeline()
    run_analytics_pipeline()
