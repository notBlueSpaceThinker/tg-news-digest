from pipeline.scraper.core_utils import AbstractCrawler, make_request, parse_and_format_pub_date
from requests.exceptions import RequestException
from bs4 import BeautifulSoup, Tag
from config import TODAY_DATE


class NNCrawler(AbstractCrawler):
    """
    Crawler for collecting fresh links from the NN.ru portal.
    https://www.nn.ru/

    """

    crawler_type: str = "nnru"

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

        soup = BeautifulSoup(response.text, features="lxml")
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