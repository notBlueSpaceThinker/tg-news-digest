from pipeline.pipeline import run_full_pipeline
from pipeline.stats_visualisation import statistic
# from api import bot
from utils import io


def main() -> None:
    run_full_pipeline()
    # _, texts = zip(*io.TextFileHandler("lemmatized").yield_all())
    # a = count_words(texts)
    # print(a)
    # max_key = max(a, key=lambda k: a[k])
    # print(max_key, a[max_key])
    _, zero = zip(*io.JsonFileHandler("zero-shot").yield_all())
    print(statistic.count_topics(zero))
    _, ner = zip(*io.JsonFileHandler("ner").yield_all())
    a = statistic.count_persons(ner)
    print(a)
    max_key = max(a, key=lambda k: a[k])
    print(a)
    print(max_key)

    

if __name__ == "__main__":
    main()
