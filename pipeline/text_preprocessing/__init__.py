import nltk


def setup_nltk() -> None:
    try:
        nltk.data.find("punkt_tab")
    except LookupError:
        nltk.download("punkt_tab")

    try:
        nltk.data.find("stopwords")
    except LookupError:
        nltk.download("stopwords")

    try:
        nltk.data.find("wordnet")
    except LookupError:
        nltk.download("wordnet")

    try:
        nltk.data.find("maxent_ne_chunker_tab")
    except LookupError:
        nltk.download("maxent_ne_chunker_tab")

    try:
        nltk.data.find("words")
    except LookupError:
        nltk.download("words")

setup_nltk()
