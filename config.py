from datetime import date
from pathlib import Path

TODAY_DATE = date.today()


ROOT_PATH = Path(__file__).parent
DATA_PATH = ROOT_PATH / "data"

DATA_RAW_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "raw"
DATA_META_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "meta"
DATA_CLEANED_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "cleaned"
DATA_LEMMATIZED_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "lemmatized"


SCRAPING_CONFIG = ROOT_PATH / "pipeline" / "scraping" / "scraper_config.json"
