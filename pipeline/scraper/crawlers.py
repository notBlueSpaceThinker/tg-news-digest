from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from config import TODAY_DATE
from pipeline.scraper.core_utils import (ScrapingConfig, WrongCrawlerType,
                                         make_request,
                                         parse_and_format_pub_date)


class BaseCrawler:
    """
    Base class for crawlers.

    Each child class should implement "crawler_type" attribute.
    """
    crawler_type: str = ""

    def __init__(self, config: ScrapingConfig) -> None:
        """
        Initialize crawler and validate crawler type.

        Raises:
            WrongCrawlerType: If "crawler_type" not in "config.rss_urls".
        """
        self.config = config
        rss_url = config.rss_urls.get(self.crawler_type, "")
        if not rss_url:
            raise WrongCrawlerType("Wrong crawler type")
        self._rss_url = rss_url

    def find_urls(self) -> list[str]:
        """
        Request to rss-url of NN.ru portal and collect current day urls.

        Returns:
            List[str]: List of urls of current day for further parsing.
        """
        try:
            response = make_request(self._rss_url, self.config)
        except RequestException:
            return []

        if not response.ok:
            return []

        soup = BeautifulSoup(response.text, features="lxml-xml")
        items = soup.find_all("item")

        found_urls = []
        for item in items:
            pub_date_tag = item.find("pubDate")
            link_tag = item.find("link")
            if not pub_date_tag or not link_tag:
                continue

            try:
                item_date = parse_and_format_pub_date(pub_date_tag.text.strip())
            except ValueError:
                continue
            if item_date == TODAY_DATE:
                found_urls.append(link_tag.text.strip())
            elif item_date < TODAY_DATE:
                break

        return found_urls


class NNCrawler(BaseCrawler):
    """
    Crawler for collecting fresh links from the nn.ru portal.
    https://www.nn.ru/

    """
    crawler_type: str = "nnru"

class NIANNCrawler(BaseCrawler):
    """
    Crawler for collecting fresh links from the niann.ru portal.
    https://www.niann.ru/

    """
    crawler_type: str = "niannru"


class NNEWSCrawler(BaseCrawler):
    """
    Crawler for collecting fresh links from the nnews.nnov.ru portal.
    https://nnews.nnov.ru/

    """
    crawler_type: str = "nnewsnnovru"
