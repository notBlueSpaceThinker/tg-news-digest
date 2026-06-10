from datetime import date, timedelta
from pathlib import Path

from environs import Env
from environs.exceptions import EnvError

TODAY_DATE = date.today() - timedelta(days=0)

ROOT_PATH = Path(__file__).parent
DATA_PATH = ROOT_PATH / "data"

DATA_RAW_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "raw"
DATA_META_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "meta"
DATA_CLEANED_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "cleaned"
DATA_LEMMATIZED_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "lemmatized"
DATA_NER_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "ner"
DATA_ZERO_SHOT_PATH = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "zero-shot"
DATA_STATS = ROOT_PATH / DATA_PATH / str(TODAY_DATE) / "stats"

DATA_PATHS = {
    "raw": DATA_RAW_PATH,
    "meta": DATA_META_PATH,
    "cleaned": DATA_CLEANED_PATH,
    "lemmatized": DATA_LEMMATIZED_PATH,
    "ner": DATA_NER_PATH,
    "zero-shot": DATA_ZERO_SHOT_PATH,
    "stats": DATA_STATS
}

SCRAPING_CONFIG = ROOT_PATH / "pipeline" / "scraping" / "scraper_config.json"

MODELS_CONFIG = ROOT_PATH / "pipeline" / "inference" / "models_config.json"

HF_TOKEN = None
API_TOKEN = None

try:
    env = Env()
    env.read_env(ROOT_PATH / ".env")
    HF_TOKEN = env("HF_TOKEN")
    API_TOKEN = env("API_TOKEN")
except EnvError:
    pass

COLOR = "#56334B"
COLOR_MAP = "RdPu"

PIPELINE_TIME_SLEEP = 60 * 15
