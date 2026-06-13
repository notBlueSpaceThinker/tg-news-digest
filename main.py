import threading
import time

from api import bot
from config import PIPELINE_TIME_SLEEP
from pipeline.pipeline import run_full_pipeline


def pipeline_loop() -> None:
    """
    Runs the infinite loop of the pipeline with certain sleep time interval.
    """
    while True:
        run_full_pipeline()
        time.sleep(PIPELINE_TIME_SLEEP)


def main() -> None:
    """
    Entrypoint for bot and pipeline.
    Starts the background pipeline thread and runs the bot polling loop.
    """
    # pipeline_loop()
    threading.Thread(target=pipeline_loop, daemon=True).start()
    bot.bot.polling(non_stop=True, timeout=20, long_polling_timeout=15)
    
    
if __name__ == "__main__":
    main()
