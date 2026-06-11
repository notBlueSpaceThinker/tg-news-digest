import matplotlib
import matplotlib.pyplot as plt
import squarify
from matplotlib.figure import Figure
from wordcloud import WordCloud

from config import COLOR_MAP

matplotlib.use('Agg')

TOPIC_TRANSLATION = {
    "entertainment": "Развлечения",
    "incidents": "Происшествия",
    "weather": "Погода",
    "art": "Искусство",
    "education": "Образование",
    "memes": "Мемы",
    "war": "Военные действия",
    "celebrities": "Знаменитости",
    "food": "Еда",
    "politics": "Политика",
    "healthcare": "Здравоохранение",
    "culture": "Культура",
    "sports": "Спорт",
    "economics": "Экономика",
    "city-life": "Городская жизнь",
    "science-and-technology": "Наука и технологии",
    "miscellaneous": "Разное"
}


def visualize_treemap(frequencies: dict[str, int], plot: bool = False) -> Figure:
    """
    Create a treemap from frequencies dict.

    Args:
        frequencies (dict[str, int]): Keys as labels and frequencies as values.
        plot (bool, optional): Display the diagram or not.
            Defaults to False.

    Returns:
        Figure: A matplotlib figure object.
    """
    topics_ru = [
        f"{TOPIC_TRANSLATION.get(topic, topic)}\n({count})"
        for topic, count in frequencies.items()
    ]
    num_colors = len(frequencies)
    fig, ax = plt.subplots(figsize=(12, 6))
    squarify.plot(
        sizes=list(frequencies.values()),
        label=topics_ru,
        color=[
            plt.get_cmap(COLOR_MAP)(0.3 + (i / num_colors) * 0.5)
            for i in range(num_colors)
        ],
        text_kwargs={
            "fontname": "Arial",
            "color": "white",
            "weight": "bold",
            "fontsize": 15
        },
        ax=ax
    )
    ax.axis("off")
    if plot:
        plt.show()
    return fig

def visualize_wordcloud(frequencies: dict[str, int], plot: bool = False) -> Figure:
    """
    Create a wordcloud from frequencies dict.

    Args:
        frequencies (dict[str, int]): Keys as labels and frequencies as values.
        plot (bool, optional): Display the diagram or not.
            Defaults to False.

    Returns:
        Figure: A matplotlib figure object.
    """
    wordcloud = WordCloud(
        width=1200,
        height=600,
        colormap=COLOR_MAP,
        background_color="white"
    )
    wordcloud.generate_from_frequencies(frequencies)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud)
    ax.axis("off")
    if plot:
        plt.show()
    return fig