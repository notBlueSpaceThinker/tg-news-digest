from bs4 import BeautifulSoup

from pipeline.scraping.core_utils import (
    ScrapingConfig,
    make_request,
    parse_date_to_datetime
)


class BaseParser():
    """
    Base class for parsers.

    Each child class should implement "parse_raw_text"
    and "parse_meta_data" functions.
    """
    def __init__(self, full_url: str, config: ScrapingConfig) -> None:
        """
        Initialize the parser and fetch the page content.

        Args:
            full_url (str): The absolute URL of the page to be parsed.
            config (ScrapingConfig): Configuration.
        """
        self.full_url = full_url
        self._config = config
        response = make_request(full_url, config)
        self.soup = BeautifulSoup(response.text, features="lxml")

    def parse_raw_text(self) -> str:
        """
        Extract the text content from the parsed HTML.

        Raises:
            NotImplementedError: If the child class does not implement this method.

        Returns:
            str: Extracted raw text of the article.
        """
        raise NotImplementedError(
            f"Method should be implemented in child class: {self.parse_raw_text.__name__}"
        )

    def parse_meta_data(self) -> dict:
        """
        Extract metadata from the parsed HTML.

        Raises:
            NotImplementedError: If the child class does not implement this method.

        Returns:
            dict: A dictionary containing metadata.
        """
        raise NotImplementedError(
            f"Method should be implemented in child class: {self.parse_meta_data.__name__}"
        )

class NNParser(BaseParser):
    """
    Parser for extracting raw text and metadata from the nn.ru portal.
    https://www.nn.ru/

    """
    def parse_raw_text(self) -> str:
        text = []
        content_divs = self.soup.find_all("div", id=["articleBody"])
        for div in content_divs:
            text_blocks = div.find_all(attrs={"data-article-block-text": True})
            for block in text_blocks:
                text.append(block.get_text())

        return " ".join(text)

    def parse_meta_data(self) -> dict:
        content_header = self.soup.find("header", attrs={"name": "articleHeader"})
        if not content_header:
            return {
                "portal": "NN.ru",
                "url": self.full_url,
                "title": None,
                "date": None,
            }

        title_tag = content_header.find("h1", id="article-title")
        title = title_tag.get_text(strip=True) if title_tag else None
        
        time_tag = content_header.find("time")
        date = time_tag.get("datetime") if time_tag else None

        return {
            "portal": "NN.ru",
            "url": self.full_url,
            "title": title,
            "date": parse_date_to_datetime(date),
        }


class NIANNParser(BaseParser):
    """
    Parser for extracting raw text and metadata from the niann.ru portal.
    https://www.niann.ru/

    """
    def parse_raw_text(self) -> str:
        text = []
        content_divs = self.soup.find_all("div", class_=["article"])
        for div in content_divs:
            text_blocks = div.find_all("p")
            for block in text_blocks:
                if "site_copyright_art" in block.attrs.get("class", []):
                    continue
                text.append(block.get_text())
        return " ".join(text)

    def parse_meta_data(self) -> dict:
        content_header = self.soup.find("div", class_=["mainheader"])
        if not content_header:
            return {
                "portal": "NIANN.ru",
                "url": self.full_url,
                "title": None,
                "date": None,
            }
        title_tag = content_header.find("h1", class_=["header"])
        title = title_tag.get_text(strip=True) if title_tag else None
        time_tag = content_header.find("span", class_=["date_standart"])
        date = time_tag.get_text(strip=True) if time_tag else None

        return {
            "portal": "NIANN.ru",
            "url": self.full_url,
            "title": title,
            "date": parse_date_to_datetime(date),
        }

class NNEWSParser(BaseParser):
    """
    Parser for extracting raw text and metadata from the nnews.nnov.ru portal.
    https://nnews.nnov.ru/

    """
    def parse_raw_text(self) -> str:
        text = []
        content_divs = self.soup.find_all("div", class_=["post-content"])
        for div in content_divs:
            text_blocks = div.find_all("p")
            for block in text_blocks:
                text.append(block.get_text())
        return " ".join(text)

    def parse_meta_data(self) -> dict:
        content_header = self.soup.find("div", class_=["title-post"])
        if not content_header:
            return {
                "portal": "NNEWS.nnov.ru",
                "url": self.full_url,
                "title": None,
                "date": None,
            }
        title_tag = content_header.find("ul", class_=["post-tags"])
        title = title_tag.get_text(strip=True) if title_tag else None
        time_tag = content_header.find("h1")
        date = time_tag.get_text(strip=True) if time_tag else None

        return {
            "portal": "NNEWS.nnov.ru",
            "url": self.full_url,
            "title": title,
            "date": parse_date_to_datetime(date),
        }
