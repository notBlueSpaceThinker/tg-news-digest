from datetime import date
from pathlib import Path

TODAY_DATE = date.today()


ROOT_PATH = Path(__file__).parent
DATA_PATH = ROOT_PATH / "data"
DATA_RAW_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "raw"
DATA_META_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "meta"
DATA_PROCESSED_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "processed"

CRAWLER_CONFIG = ROOT_PATH / "pipeline" / "scraper" / "scraper_config.json"

