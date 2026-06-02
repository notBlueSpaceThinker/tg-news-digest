import hashlib
import json

from config import DATA_META_PATH, DATA_PATH, DATA_RAW_PATH, TODAY_DATE


HASHED_URLS_JSON = DATA_PATH / str(TODAY_DATE) / "hashed_urls.json"

def ensure_data_paths() -> None:
    """
    Create directiories if they do not exist.
    """
    DATA_META_PATH.mkdir(parents=True, exist_ok=True)
    DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)


def hash_url(url: str) -> str:
    """
    Generate a unique SHA-256 hash string for a given URL.

    Args:
        url (str): Target URL.

    Returns:
        str: A 64-character hexadecimal SHA-256 hash string.
    """
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

def load_from_meta():
    """_summary_
    """
    pass

def save_to_meta():
    """_summary_
    """
    pass

