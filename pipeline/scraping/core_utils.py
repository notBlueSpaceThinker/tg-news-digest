import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import requests


@dataclass
class ScrapingConfig:
    """
    Configuration for crawlers.
    Stores common settings for requestng and parsing.
    """
    headers: dict = field(default_factory=dict)
    rss_urls: dict = field(default_factory=dict)
    encoding: str = "utf-8"
    timeout: int = 10

    @classmethod
    def load_config(cls, path_to_config: Path | str) -> "ScrapingConfig":
        """
        Load scraping configurations from a JSON file.

        Args:
            path_to_config (Path | str): Path to the JSON config file.

        Returns:
            ScrapingConfig: An instance of the class with loaded data.
        """
        with open(path_to_config, "r", encoding="utf-8") as file:
            config_data = json.load(file)

        return cls(
            headers=config_data.get("headers", {}),
            rss_urls=config_data.get("rss_urls", {}),
            encoding=config_data.get("encoding", "utf-8"),
            timeout=config_data.get("timeout", 10)
        )


class WrongCrawlerType(Exception):
    """
    Raised then crawler type is not found in config.
    """


def make_request(url: str, config: ScrapingConfig) -> requests.models.Response:
    """
    Deliver a response from a request with given configuration.

    Args:
        url (str): Site url.
        config (ScrapingConfig): Configuration.

    Returns:
        requests.models.Response: A response from a request.
    """
    response = requests.get(
        url=url,
        headers=config.headers,
        timeout=config.timeout,
    )
    response.encoding = config.encoding
    return response


def parse_and_format_pub_date(pub_date: str) -> date:
    """
    Parse pub_date from rss format into a date object.

    Args:
        pub_date (str): The raw publication date string extracted from the rss.

    Raises:
        ValueError: If the input string does not match any supported date formats.

    Returns:
        date: A datetime.date object.
    """
    try:
        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        return dt.date()
    except Exception:
        pass

    try:
        dt = datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S %z")
        return dt.date()
    except ValueError:
        pass

    raise ValueError

def parse_date_to_datetime(date_str) -> str | None:
    if not date_str:
        return None
    if "T" in date_str:
        return date_str
    months = {
        "января": "01", "февраля": "02", "марта": "03",
        "апреля": "04", "мая": "05", "июня": "06",
        "июля": "07", "августа": "08", "сентября": "09",
        "октября": "10", "ноября": "11", "декабря": "12"
    }
    for month, num_month in months.items():
        if month in date_str:
            try:
                return datetime.strptime(
                    date_str.replace(month, num_month),
                    "%d %m %Y %H:%M"
                ).isoformat()
            except ValueError:
                return None
        
    if "." in date_str:
        try:
            return datetime.strptime(
                date_str,
                "%d.%m.%Y %H:%M"
            ).isoformat()
        except ValueError:
            return None
        
    return None
