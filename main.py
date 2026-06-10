import threading
import time

from api import bot
from config import PIPELINE_TIME_SLEEP
from pipeline.pipeline import run_full_pipeline


def pipeline_loop():
    while True:
        run_full_pipeline()
        time.sleep(PIPELINE_TIME_SLEEP)

def main() -> None:
    threading.Thread(target=pipeline_loop, daemon=True).start()
    bot.bot.polling(non_stop=True)
    
    
if __name__ == "__main__":
    main()
