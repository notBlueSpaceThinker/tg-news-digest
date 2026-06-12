from collections import Counter
from collections.abc import Iterable
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import math
import re

from pipeline.preprocessing import preprocessing
from utils import io

stats_handler = io.JsonFileHandler("stats")

STOP_WORDS = {
    'и', 'в', 'на', 'с', 'по', 'к', 'у', 'за', 'из', 'о', 'об', 'от', 'до',
    'для', 'без', 'через', 'над', 'под', 'при', 'между', 'это', 'было', ...
}

COLLOCATION_CONFIG = {
    "window_size": 5,           # Размер окна для co-occurrence (совместное появление слов в тексте)
    "min_word_freq": 3,         # Минимальная частота слова для LogDice
    "min_cooccurrence": 2,      # Минимальная частота ковстречаемости
    "filter_stop_words": True,  # Фильтровать стоп-слова
    "min_word_length": 3,       # Минимальная длина слова
    "top_n_trigrams": 10,
    "top_n_logdice": 10,
}

def filter_words(words: List[str], min_length: int = 3, remove_stop_words: bool = True) -> List[str]:
    """
    Filter words by length and stop words.

    Args:
    words: List of words to filter
    min_length: Minimum word length
    remove_stop_words: Whether to remove stop words

    Returns:
    The filtered list of words
    """
    filtered = []
    for word in words:
        if len(word) < min_length:
            continue
        if remove_stop_words and word.lower() in STOP_WORDS:
            continue
        filtered.append(word)
    return filtered


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
        news_list.append(f"{key}. {meta['portal']}: {meta['title']}")
        time = datetime.fromisoformat(meta["date"]).time()
        news_list.append(f"_Время публикации: {time}\n_")
        urls.append(meta["url"])
    return  "\n".join(news_list)


def extract_word_trigrams_from_text(text: str, filter_stop_words: bool = True) -> List[str]:
    """
    Extract word trigrams from text.
    
    Args:
        text (str): Input text.
        
    Returns:
        List[str]: List of word trigrams (sequences of 3 words).
    """
    words = preprocessing.tokenize_by_words(text)
    if filter_stop_words:
        words = filter_words(
            words,
            min_length=COLLOCATION_CONFIG["min_word_length"],
            remove_stop_words=True
        )
    
    word_trigrams = []
    for i in range(len(words) - 2):
        trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
        word_trigrams.append(trigram)
    
    return word_trigrams

def calculate_logdice(cooccurrence_count: int, freq_word1: int, freq_word2: int) -> float:
    """
    Calculate LogDice coefficient for two words.
    
    Formula: logDice = 14 + log10(2 * f(w1,w2) / (f(w1) + f(w2)))
    
    Args:
        cooccurrence_count (int): Frequency of word1 and word2 appearing together.
        freq_word1 (int): Frequency of word1 in the corpus.
        freq_word2 (int): Frequency of word2 in the corpus.
        
    Returns:
        float: LogDice coefficient (range ~0-14, higher = stronger association).
    """
    if freq_word1 + freq_word2 == 0:
        return 0.0

    dice = (2 * cooccurrence_count) / (freq_word1 + freq_word2)

    if dice > 0:
        logdice = 14 + math.log10(dice)
    else:
        logdice = 0.0

    return logdice

def count_word_trigrams(texts: Iterable[str]) -> dict:
    """
    Count word trigram frequencies across a collection of texts.
    
    Args:
        texts (Iterable[str]): Collection of texts to process.
        
    Returns:
        dict: With trigrams as keys and their occurrence counts as values.
    """
    trigram_frequencies = Counter()
    
    for text in texts:
        trigrams = extract_word_trigrams_from_text(text, COLLOCATION_CONFIG["filter_stop_words"])
        trigram_frequencies.update(trigrams)
    
    return dict(trigram_frequencies)

def count_cooccurrences(texts: Iterable[str], window_size: int = 5, filter_stop_words: bool = True) -> Dict[Tuple[str, str], int]:
    """
    Count word cooccurrences within a sliding window.
    
    Args:
        texts (Iterable[str]): Collection of texts.
        window_size (int): Window size for cooccurrence (default 5).
        
    Returns:
        dict: With word pairs as keys and cooccurrence counts as values.
    """
    cooccurrence_matrix = Counter()
    
    for text in texts:
        words = preprocessing.tokenize_by_words(text)

        if filter_stop_words:
            words = filter_words(
                words,
                min_length=COLLOCATION_CONFIG["min_word_length"],
                remove_stop_words=True
            )
        
        for i in range(len(words)):
            for j in range(i + 1, min(i + window_size + 1, len(words))):
                word_pair = tuple(sorted([words[i], words[j]]))
                cooccurrence_matrix[word_pair] += 1
    
    return dict(cooccurrence_matrix)

def calculate_logdice_for_corpus(
    texts: Iterable[str], 
    window_size: int = 5,
    min_word_freq: int = 3,
    min_cooccurrence: int = 2,
    filter_stop_words: bool = True
) -> List[Tuple[str, float, Dict]]:
    """
    Calculate LogDice scores for all cooccurring word pairs in the corpus.
    
    Args:
        texts (Iterable[str]): Collection of texts.
        window_size (int): Window size for cooccurrence.
        min_word_freq (int): Minimum word frequency to consider.
        min_cooccurrence (int): Minimum cooccurrence frequency to consider.
        filter_stop_words (bool): Whether to filter out stop words.
        
    Returns:
        List[Tuple[str, float, Dict]]: List of (word_pair, logdice_score, metadata).
    """
    word_frequencies = count_words(texts)
    cooccurrence_matrix = count_cooccurrences(texts, window_size, filter_stop_words)
    
    results = []
    for (word1, word2), cooccurrence_count in cooccurrence_matrix.items():
        freq1 = word_frequencies.get(word1, 0)
        freq2 = word_frequencies.get(word2, 0)

        if freq1 < min_word_freq or freq2 < min_word_freq:
            continue
        if cooccurrence_count < min_cooccurrence:
            continue
        
        logdice_score = calculate_logdice(cooccurrence_count, freq1, freq2)

        results.append((
            f"{word1} — {word2}",
            logdice_score,
            {
                "freq1": freq1,
                "freq2": freq2,
                "cooccurrence": cooccurrence_count,
                "dice": (2 * cooccurrence_count) / (freq1 + freq2)
            }
        ))
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def get_word_trigram_frequencies(top_n: Optional[int] = 5) -> List[Tuple]:
    """
    Get top word trigram frequencies from saved stats.
    
    Args:
        top_n (Optional[int]): Number of top trigrams to return.
        
    Returns:
        List[Tuple]: List of (trigram, frequency) tuples.
    """
    trigram_frequencies = stats_handler.load("word_trigram_frequencies", load_hashed=False)
    
    if not trigram_frequencies:
        return []
    
    trigram_frequencies = sorted(
        trigram_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    if top_n:
        return trigram_frequencies[:top_n]
    return trigram_frequencies


def get_logdice_scores(top_n: Optional[int] = 10) -> List[Tuple]:
    """
    Get top LogDice scores from saved stats.
    
    Args:
        top_n (Optional[int]): Number of top scores to return.
        
    Returns:
        List[Tuple]: List of (word_pair, logdice_score) tuples.
    """
    logdice_scores = stats_handler.load("logdice_scores", load_hashed=False)
    
    if not logdice_scores:
        return []


    if top_n:
        return logdice_scores[:top_n]
    return logdice_scores

def update_collocation_statistics(texts: Iterable[str]) -> None:
    """
    Update collocation statistics (word trigrams and LogDice).
    
    Args:
        texts (Iterable[str]): Collection of texts to process.
    """

    print("Анализ коллокаций...")

    word_trigram_frequencies = count_word_trigrams(texts)
    stats_handler.save(word_trigram_frequencies, "word_trigram_frequencies", save_hashed=False)

    logdice_results = calculate_logdice_for_corpus(
        texts,
        window_size=COLLOCATION_CONFIG["window_size"],
        min_word_freq=COLLOCATION_CONFIG["min_word_freq"],
        min_cooccurrence=COLLOCATION_CONFIG["min_cooccurrence"],
        filter_stop_words=COLLOCATION_CONFIG["filter_stop_words"]
    )
    stats_handler.save(logdice_results, "logdice_scores", save_hashed=False)

    top_trigrams = sorted(
        word_trigram_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )[:COLLOCATION_CONFIG["top_n_trigrams"]]
    stats_handler.save(top_trigrams, "top_word_trigrams", save_hashed=False)
    
    top_logdice = logdice_results[:COLLOCATION_CONFIG["top_n_logdice"]]
    stats_handler.save(top_logdice, "top_logdice_scores", save_hashed=False)
    
    print(f"  Сохранено {len(word_trigram_frequencies)} уникальных триграмм")
    print(f"  Сохранено {len(logdice_results)} пар с LogDice")


def get_collocation_summary(top_n: int = 5) -> str:
    """
    Get a formatted summary of collocation statistics.
    
    Args:
        top_n (int): Number of top items to show.
        
    Returns:
        str: Formatted summary string.
    """
    summary_parts = []


    word_trigrams = get_word_trigram_frequencies(top_n)
    if word_trigrams:
        summary_parts.append("Топ словесных триграмм:")
        for i, (trigram, freq) in enumerate(word_trigrams, 1):
            summary_parts.append(f"  {i:2}. '{trigram}' → {freq} раз(а)")
    else:
        summary_parts.append("\nНет данных по триграммам")


    logdice_scores = get_logdice_scores(top_n)
    if logdice_scores:
        summary_parts.append("\nТоп пар слов по LogDice:")
        for i, item in enumerate(logdice_scores, 1):
                    if len(item) == 3:
                        pair, score, _ = item
                        summary_parts.append(f"  {pair}: {score:.3f}")
                    else:
                        pair, score = item
                        summary_parts.append(f"  {pair}: {score:.3f}")
    else:
        summary_parts.append("\nНет данных по LogDice")


    return "\n".join(summary_parts)