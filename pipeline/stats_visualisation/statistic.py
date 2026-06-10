from collections import Counter
from collections.abc import Iterable

from nltk.tokenize import word_tokenize

from pipeline.preprocessing.preprocessing import normalize_name, word_tokenize


def count_words(texts: Iterable[str]) -> dict:
    word_frequencies = Counter()
    for text in texts:
        word_frequencies.update(word_tokenize(text))
    return word_frequencies

def count_topics(zero_shot_predictions: Iterable[dict]) -> dict:
    topic_frequencies = Counter()
    for prediction in zero_shot_predictions:
        topic, _ = max(
            zip(prediction["labels"], prediction["scores"]),
            key=lambda item: item[1]
        )
        topic_frequencies[topic] += 1
    return topic_frequencies

def count_persons(ner_predictions: Iterable[dict]) -> dict:
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
                first_name_normalized = normalize_name(current['word'], 'name')
                last_name_normalized = normalize_name(next_entity['word'], 'surn')
                person_frequencies[f"{first_name_normalized} {last_name_normalized}"] += 1
                i += 2
                continue
            i += 1
    return person_frequencies
