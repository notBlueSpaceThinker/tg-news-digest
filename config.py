from pathlib import Path
from datetime import date


ROOT_PATH = Path(__file__).parent
DATA_PATH = ROOT_PATH / "data"
DATA_RAW_PATH = ROOT_PATH / DATA_PATH / "raw"
DATA_PROCESSED_PATH = ROOT_PATH / DATA_PATH / "processed"

TODAY_DATE = str(date.today())