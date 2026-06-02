import re
from string import punctuation

import nltk
import pymorphy3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find("corpora/stopwords")
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt_tab", quiet=True)


STOP_WORDS = stopwords.words("russian")
morph = pymorphy3.MorphAnalyzer(lang='ru')

def tokenize_by_words(text: str) -> list[str]:
    """
    Split text str to word tokens.

    Args:
        text (str): The input text string.

    Returns:
        list[str]: A list of extracted word tokens.
    """
    return nltk.word_tokenize(text)


def tokenize_by_sentences(text: str) -> list[str]:
    """
    Split text str to sentence tokens.

    Args:
        text (str): The input text string.

    Returns:
        list[str]: A list of extracted sentence tokens.
    """
    return nltk.sent_tokenize(text)


def clean(text: str) -> str:
    """
    Process text cleaning, removing HTML artifacts, URLs,
    emojis and punctuation.

    Args:
        text (str): The input text string.

    Returns:
        str: The cleaned lowercase text.
    """
    text = text.lower()
    html_pattern = re.compile(r"&[a-z0-9#]+;")
    text = html_pattern.sub(r"", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub(r"", text)
    remove_punct = str.maketrans("", "", punctuation)
    text = text.translate(remove_punct)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_stop_words(tokens: list[str], concat: bool = False) -> str | list[str]:
    """
    Remove Russian stop words form a given list of tokens.

    Args:
        tokens (list[str]): A list of word tokens to remove stop words.
        concat (bool, optional): If true, returns space-separated string.
            If false, returns list of input tokens. Defaults to False.

    Returns:
        str | list[str]: Space-separated str or a list of tokens.
    """
    removed_stop_words = [
            token
            for token in tokens
            if token not in STOP_WORDS
        ]
    return " ".join(removed_stop_words) if concat else removed_stop_words


def lemmatize(tokens: list[str], concat: bool = False) -> str | list[str]:
    """
    Lemmatize a given list of tokens

    Args:
        tokens (list[str]): A list of word tokens to lemmatize.
        concat (bool, optional): If true, returns space-separated string.
            If false, returns list of input tokens. Defaults to False.

    Returns:
        str | list[str]: Space-separated str or a list of tokens.
    """
    lemmatized = [
            morph.parse(word)[0].normal_form
            for word in tokens
        ]
    return " ".join(lemmatized) if concat else lemmatized
