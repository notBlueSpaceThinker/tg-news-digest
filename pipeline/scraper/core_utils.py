import json
from abc import ABC, abstractmethod
import requests
from dataclasses import dataclass, field
from pathlib import Path
from datetime import date, datetime

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
    Raised then crawler type is not found in config
    """


class AbstractCrawler(ABC):
    """
    Abstract basic class for crawlers.

    Each child class should implement "crawler_type" attribute and
    implement "find_urls" function
    """
    crawler_type: str = ""

    def __init__(self, config: ScrapingConfig) -> None:
        """
        Initialize crawler and validate crawler type

        Raises:
            WrongCrawlerType: If "crawler_type" not in "config.rss_urls"
        """
        super().__init__()
        self.config = config
        rss_url = config.rss_urls.get(self.crawler_type, "")
        if not rss_url:
            raise WrongCrawlerType("Wrong crawler type")
        self._rss_url = rss_url

    @abstractmethod
    def find_urls(self) -> list:
        """
        Request to rss-url and collect current day urls

        Returns:
            list[str]: List of urls of current day for further parsing
        """
        pass


def make_request(url: str, config: ScrapingConfig) -> requests.models.Response:
    """
    Deliver a response from a request with given configuration.

    Args:
        url (str): Site url
        config (Config): Configuration

    Returns:
        requests.models.Response: A response from a request
    """
    response = requests.get(
        url=url,
        headers=config.headers,
        timeout=config.timeout,
    )

    return response

def parse_and_format_pub_date(pub_date: str) -> date:
    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
    return dt.date()