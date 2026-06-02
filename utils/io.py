import hashlib
import json
import re
from collections.abc import Iterable

from config import (DATA_CLEANED_PATH, DATA_LEMMATIZED_PATH, DATA_META_PATH,
                    DATA_PATH, DATA_RAW_PATH, TODAY_DATE)

HASHED_URLS_JSON = DATA_PATH / str(TODAY_DATE) / "hashed_urls.json"

def ensure_data_paths() -> None:
    """
    Create directiories if they do not exist.
    """
    DATA_META_PATH.mkdir(parents=True, exist_ok=True)
    DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)
    DATA_CLEANED_PATH.mkdir(parents=True, exist_ok=True)
    DATA_LEMMATIZED_PATH.mkdir(parents=True, exist_ok=True)


def hash_url(url: str) -> str:
    """
    Generate a unique SHA-256 hash string for a given URL.

    If the input string matches the pattern of a valid SHA-256 hex hash,
    it returns it to prevent double-hashing.
    Args:
        url (str): Target URL.

    Returns:
        str: A 64-character hexadecimal SHA-256 hash string.
    """
    if re.match(r"^[0-9a-fA-F]{64}$", url):
        return url

    return hashlib.sha256(url.encode()).hexdigest()


def load_url_from_hash(hash: str) -> str | None:
    """
    Get the original URL from daily json.

    Args:
        hash (str): The 64-character SHA-256 hash string.

    Returns:
        str | None: The original url if found in json.
    """
    with open(HASHED_URLS_JSON, "r", encoding="utf-8") as file:
        storage = json.load(file)
    return storage.get(hash)


def save_url_to_hash(url: str) -> str:
    """
    Save a url-to-hash mapping.

    Reads and updates existing json, representing daily articles.
    Automatically creates the json if missing.

    Args:
        url (str): Target URL.

    Returns:
        str: The generated 64-character SHA-256 hash string.
    """
    storage = {}
    try:
        with open(HASHED_URLS_JSON, "r", encoding="utf-8") as file:
            storage = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    hashed_url = hash_url(url)
    storage[hashed_url] = url
    with open(HASHED_URLS_JSON, "w", encoding="utf-8") as file:
        json.dump(storage, file)

    return hashed_url


def load_from_raw(url: str) -> str:
    """
    Load the saved raw article, using URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The raw text extracted from the corresponding file.
    """
    hashed_url = hash_url(url)
    with open(DATA_RAW_PATH / f"{hashed_url}.txt", "r", encoding="utf-8") as file:
        return file.read()

def save_to_raw(url: str, text: str) -> str:
    """
    Save the raw text to a txt file and get it hashed name.

    Args:
        url (str): The URL of the article.
        text (str): The raw text of the article.

    Returns:
        str: The generated 64-character SHA-256 hash string.
    """
    hashed_url = hash_url(url)
    with open(DATA_RAW_PATH / f"{hashed_url}.txt", "w", encoding="utf-8") as file:
        file.write(text)
    return hashed_url

def get_raw_texts() -> Iterable:
    """
    Iterates over DATA_RAW_PATH and yields hashed urls and
    corresponding texts.

    Yields:
        Iterator[Iterable]: Hashed url with corresponding raw text.
    """
    for file_path in DATA_RAW_PATH.glob("*.txt"):
        url_hash = file_path.stem
        with open(file_path, "r", encoding="utf-8") as file:
            yield (url_hash, file.read())


def load_from_meta() -> dict:
    """_summary_
    """
    pass

def save_to_meta(url: str, meta: dict) -> str:
    """_summary_
    """
    pass

def get_meta_datas() -> Iterable:
    """
    Iterates over DATA_META_PATH and yields hashed urls and
    corresponding meta jsons.

    Yields:
        Iterator[Iterable]: Hashed url with corresponding meta data.
    """
    for file_path in DATA_META_PATH.glob("*.json"):
        url_hash = file_path.stem
        with open(file_path, "r", encoding="utf-8") as file:
            yield (url_hash, json.load(file))


def load_from_cleaned(url: str) -> str:
    """
    Load the saved cleaned article, using URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The cleaned text extracted from the corresponding file.
    """
    hashed_url = hash_url(url)
    with open(DATA_CLEANED_PATH / f"{hashed_url}.txt", "r", encoding="utf-8") as file:
        return file.read()

def save_to_cleaned(url: str, text: str) -> str:
    """
    Save the cleaned text to a txt file and get it hashed name.

    Args:
        url (str): The URL of the article.
        text (str): The cleaned text of the article.

    Returns:
        str: The generated 64-character SHA-256 hash string.
    """
    hashed_url = hash_url(url)
    with open(DATA_CLEANED_PATH / f"{hashed_url}.txt", "w", encoding="utf-8") as file:
        file.write(text)
    return hashed_url

def get_cleaned_texts() -> Iterable:
    """
    Iterates over DATA_CLENED_PATH and yields hashed urls and
    corresponding texts.

    Yields:
        Iterator[Iterable]: Hashed url with corresponding cleaned text.
    """
    for file_path in DATA_CLEANED_PATH.glob("*.txt"):
        url_hash = file_path.stem
        with open(file_path, "r", encoding="utf-8") as file:
            yield (url_hash, file.read())


def load_from_lemmatized(url: str) -> str:
    """
    Load the saved lemmatized article, using URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The lemmatized text extracted from the corresponding file.
    """
    hashed_url = hash_url(url)
    with open(DATA_LEMMATIZED_PATH / f"{hashed_url}.txt", "r", encoding="utf-8") as file:
        return file.read()

def save_to_lemmatized(url: str, text: str) -> str:
    """
    Save the lemmatized text to a txt file and get it hashed name.

    Args:
        url (str): The URL of the article.
        text (str): The lemmatized text of the article.

    Returns:
        str: The generated 64-character SHA-256 hash string.
    """
    hashed_url = hash_url(url)
    with open(DATA_LEMMATIZED_PATH / f"{hashed_url}.txt", "w", encoding="utf-8") as file:
        file.write(text)
    return hashed_url

def get_lemmatized_texts() -> Iterable:
    """
    Iterates over DATA_LEMMATIZED_PATH and yields hashed urls and
    corresponding texts.

    Yields:
        Iterator[Iterable]: Hashed url with corresponding lemmatized text.
    """
    for file_path in DATA_LEMMATIZED_PATH.glob("*.txt"):
        url_hash = file_path.stem
        with open(file_path, "r", encoding="utf-8") as file:
            yield (url_hash, file.read())
