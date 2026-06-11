from collections import Counter
from collections.abc import Iterable
from datetime import datetime

from pipeline.preprocessing import preprocessing
from utils import io

stats_handler = io.JsonFileHandler("stats")

def count_words(texts: Iterable[str]) -> dict:
    """
    Count word frequencies across a collection of texts.

    Args:
        texts (Iterable[str]): Collection of texts to process.

    Returns:
        dict: With words as keys and their occurrence counts as values.
    """
    word_frequencies = Counter()
    for text in texts:
        word_frequencies.update(preprocessing.tokenize_by_words(text))
    return word_frequencies

def count_topics(zero_shot_predictions: Iterable[dict]) -> dict:
    """
    Count the frequency of predicted topics.

    Args:
        zero_shot_predictions (Iterable[dict]): Collection of zero-shot
            classification results.

    Returns:
        dict: With topics as keys and their occurrence counts as values.
    """
    topic_frequencies = Counter()
    for prediction in zero_shot_predictions:
        topic, _ = max(
            zip(prediction["labels"], prediction["scores"]),
            key=lambda item: item[1]
        )
        topic_frequencies[topic] += 1
    return topic_frequencies

def count_persons(ner_predictions: Iterable[dict]) -> dict:
    """
    Count the frequency of predicted persons.

    Args:
        ner_predictions (Iterable[dict]): Collection of NER prediction results.

    Returns:
        dict: With presons as keys and their occurrence counts as values.
    """
    person_frequencies = Counter()
    for prediction in ner_predictions:
        entities = sorted(prediction["predict"], key=lambda x: x["start"])
        i = 0
        while i < len(entities):
            current = entities[i]
            if current["entity_group"] != "FIRST_NAME":
                i += 1
                continue
            if i + 1 == len(entities):
                break
            next_entity = entities[i + 1]
            if next_entity["entity_group"] == "LAST_NAME" and next_entity["start"] <= current["end"] + 1:
                first_name_normalized = preprocessing.normalize_name(current['word'], 'name')
                last_name_normalized = preprocessing.normalize_name(next_entity['word'], 'surn')
                person_frequencies[f"{first_name_normalized} {last_name_normalized}"] += 1
                i += 2
                continue
            i += 1
    return person_frequencies

def get_word_frequencies(top_n: int | None = 5) -> list[tuple]:
    word_frequencies = stats_handler.load("word_frequencies", load_hashed=False)
    word_frequencies = sorted(
        word_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )
    if top_n:
        return word_frequencies[:top_n]
    return word_frequencies
    
def get_topic_frequencies(top_n: int | None = 5) -> list[tuple]:
    topic_frequencies = stats_handler.load("topic_frequencies", load_hashed=False)
    topic_frequencies = sorted(
        topic_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )        
    if top_n:
        return topic_frequencies[:top_n]
    return topic_frequencies

def get_person_frequencies(top_n: int | None = 5) -> list[tuple]:
    person_frequencies = stats_handler.load("person_frequencies", load_hashed=False)
    person_frequencies = sorted(
        person_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )
    if top_n:
        return person_frequencies[:top_n]
    return person_frequencies

def get_fresh_news_text(top_n: int | None = 7) -> str:
    fresh_news = stats_handler.load("fresh_news", load_hashed=False)
    sorted_keys = sorted(fresh_news.keys(), key=lambda k: int(k))
    if top_n:
        sorted_keys = sorted_keys[:top_n]
    urls = [] #дописать
    news_list = []
    for key in sorted_keys:
        meta = fresh_news[key]
        news_list.append(f"{key}. {meta["portal"]}: {meta["title"]}")
        time = datetime.fromisoformat(meta["date"]).time()
        news_list.append(f"_Время публикации: {time}\n_")
        urls.append(meta["url"])
    return  "\n".join(news_list)
