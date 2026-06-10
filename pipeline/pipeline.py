from tqdm import tqdm

from config import SCRAPING_CONFIG
from pipeline.inference.inference import run_ner, run_zero_shot
from pipeline.preprocessing.preprocessing import (clean, lemmatize,
                                                  remove_stop_words,
                                                  word_tokenize)
from pipeline.scraping.core_utils import ScrapingConfig
from pipeline.scraping.crawlers import NIANNCrawler, NNCrawler, NNEWSCrawler
from pipeline.scraping.parsers import NIANNParser, NNEWSParser, NNParser
from pipeline.stats_visualisation import statistic, visualizer
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
        for url in tqdm(urls, desc=f"Parsing {portal_name}: "):
            if raw_handler.check_if_saved(url) and \
            meta_handler.check_if_saved(url):
                continue
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
    for hashed_url, text in tqdm(raw_handler.yield_all(), desc="Text preprocessing: "):
        if cleaned_handler.check_if_saved(hashed_url) and \
        lemmatized_handler.check_if_saved(hashed_url):
            continue
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
    for hashed_url, text in tqdm(cleaned_handler.yield_all(), desc="Inference with zero-shot: "):
        if zero_shot_handler.check_if_saved(hashed_url):
            continue
        zero_shot = run_zero_shot(text)
        if not zero_shot:
            continue
        zero_shot_handler.save(hashed_url, zero_shot)

    raw_handler = io.TextFileHandler("raw")
    ner_handler = io.JsonFileHandler("ner")
    for hashed_url, text in tqdm(raw_handler.yield_all(), desc="Inference with ner: "):
        if ner_handler.check_if_saved(hashed_url):
            continue
        ner = run_ner(text)
        if not ner:
            continue
        ner_handler.save(hashed_url, ner)


def run_analytics_pipeline() -> None:
    """
    Generate corpus statistics and save visualization summary.
    """
    figure_handler = io.PngFigureHandler()
    stats_handler = io.JsonFileHandler("stats")

    _, texts = zip(*io.TextFileHandler("lemmatized").yield_all())
    word_frequencies = statistic.count_words(texts)
    fig = visualizer.visualize_wordcloud(word_frequencies)
    figure_handler.save("word_frequencies", fig)
    stats_handler.save("word_frequencies", word_frequencies, load_hashed=False)

    _, zero_shot = zip(*io.JsonFileHandler("zero-shot").yield_all())
    topic_frequencies = statistic.count_topics(zero_shot)
    fig = visualizer.visualize_treemap(topic_frequencies)
    figure_handler.save("topic_frequencies", fig)
    stats_handler.save("topic_frequencies", topic_frequencies, load_hashed=False)

    _, ner = zip(*io.JsonFileHandler("ner").yield_all())
    person_frequencies = statistic.count_persons(ner)
    fig = visualizer.visualize_wordcloud(person_frequencies)
    figure_handler.save("person_frequencies", fig)
    stats_handler.save("person_frequencies", person_frequencies, load_hashed=False)


def run_full_pipeline() -> None:
    """
    Orchestrate all the pipelines and run them.
    """
    run_scraping_pipeline()
    run_preprocessing_pipeline()
    run_inference_pipeline()
    run_analytics_pipeline()
