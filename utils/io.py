import hashlib
import json
import re
from collections.abc import Iterable
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from config import DATA_PATH, DATA_PATHS, TODAY_DATE

HASHED_URLS_JSON = DATA_PATH / str(TODAY_DATE) / "hashed_urls.json"


def ensure_data_paths() -> None:
    """
    Create directiories if they do not exist.
    """
    for path in DATA_PATHS.values():
        path.mkdir(parents=True, exist_ok=True)


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


class FileHandler:
    def __init__(
            self,
            data_path: Literal[
                "raw",
                "cleaned",
                "lemmatized",
                "meta",
                "zero-shot",
                "ner",
                "stats"
            ]
        ) -> None:
        """
        Initialize FileHandler for a certain data type

        Args:
            data_path (Literal): Data name (for instance: "raw", "meta", etc.)

        Raises:
            NotImplementedError: If given unsupported data name.
        """
        if data_path not in DATA_PATHS:
            raise NotImplementedError(
                f"The data path: {data_path} is not allowed"
            )
        self.data_path = data_path
        self.directory = DATA_PATHS[data_path]

        if self.data_path in ("raw", "cleaned", "lemmatized"):
            self.data_type = ".txt"
        elif self.data_path in ("meta", "zero-shot", "ner", "stats"):
            self.data_type = ".json"

    def load(self, filename: str, save_hashed=True) -> str | dict:
        """
        Load the saved data, using URL.

        Args:
            url (str): The URL of the article.

        Returns:
            str | dict: Data from the corresponding file.
        """### Переписать докстринг
        if save_hashed:
            filename = hash_url(filename)
        file_path = self.directory / f"{filename}{self.data_type}"
        with open(file_path, "r", encoding="utf-8") as file:
            if self.data_type == ".json":
                return json.load(file)
            return file.read()

    def save(self, filename: str, data: str | dict, load_hashed=True) -> str:
        """
        Save the data to file and get it hashed name.

        Args:
            url (str): The URL of the article.
            data (str | dict): Data for saving.

        Returns:
            str: The generated 64-character SHA-256 hash string.
        """
        if load_hashed:
            filename = hash_url(filename)
        file_path = self.directory / f"{filename}{self.data_type}"
        with open(file_path, "w", encoding="utf-8") as file:
            if self.data_type == ".json":
                if not isinstance(data, dict):
                    raise TypeError
                json.dump(data, file, indent=4, ensure_ascii=False)
            else:
                if not isinstance(data, str):
                    raise TypeError
                file.write(data)
        return filename

    def yield_all(self) -> Iterable[tuple[str, str | dict]]:
        """
        Iterates over the files from the given directory.

        Yields:
            Iterator[Iterable]: Tuple of (hashed url, data content).
        """
        for file_path in self.directory.glob(f"*{self.data_type}"):
                filename = file_path.stem                        
                with open(file_path, "r", encoding="utf-8") as file:
                    if self.data_type == ".json":
                        yield filename, json.load(file)
                    else:
                        yield filename, file.read()

    def check_if_saved(self, url: str) -> bool:
        """
        Checks if the URL is saved.

        Args:
            url (str): The URL of the article.

        Returns:
            bool: True if the file already exists, False otherwise.
        """
        hashed_url = hash_url(url)
        return (self.directory / f"{hashed_url}{self.data_type}").is_file()


class TextFileHandler(FileHandler):
    def load(self, filename: str, *args, **kwargs) -> str:
        data = super().load(filename,  *args, **kwargs)
        if not isinstance(data, str):
            raise TypeError
        return data

    def yield_all(self) -> Iterable[tuple[str, str]]:
        for filename, data in super().yield_all():
            if not isinstance(data, str):
                raise NotImplementedError
            yield filename, data


class JsonFileHandler(FileHandler):
    def load(self, filename: str, *args, **kwargs) -> dict:
        data = super().load(filename, *args, **kwargs)
        if not isinstance(data, dict):
            raise TypeError
        return data

    def yield_all(self) -> Iterable[tuple[str, dict]]:
        for filename, data in super().yield_all():
            if not isinstance(data, dict):
                raise NotImplementedError
            yield filename, data


class PngFigureHandler():
    def __init__(self, data_path: Literal["stats"] = "stats") -> None:
        if data_path not in DATA_PATHS:
            raise NotImplementedError(
                f"The data path: {data_path} is not allowed"
            )
        self.data_path = data_path
        self.directory = DATA_PATHS[data_path]
        self.data_type = ".png"

    def save(self, filename: str, fig: Figure) -> str:
        if not isinstance(fig, Figure):
            raise TypeError("Expected matplotlib.figure.Figure object")
        fig.savefig(
            self.directory / f"{filename}{self.data_type}",
            format=self.data_type.strip(".")
        )
        plt.close()
        return filename
    
    def load(self, filename) -> bytes:
        with open(self.directory / f"{filename}{self.data_type}", "rb") as file:
            return file.read()
        
    def check_if_saved(self, filename: str) -> bool:
        return (self.directory / f"{filename}{self.data_type}").is_file()

        
