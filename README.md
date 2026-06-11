# Nizhny News Bot
**This is a telegram-bot developed to generate news summaries and extract useful linguistic data**. The program itself parses local websites to collect text and metainformation, preprocesses it and performs inference using Zero-Shot and NER models. After that, it collects statistical data and passes the results to the Telegram bot api.

### Bot Commands
| Command           | Description                                                                          |
| ----------------- | ------------------------------------------------------------------------------------ |
| `/start`          | Start bot and display the welcome message                                            |
| `/help`           | Show available functionality and navigation help                                     |
| `Дайджест`        | A summary of all the information that partially shows each of the possible commands  |
| `Популярные темы` | The topic that was most frequently discussed in the media (extracted with Zero-Shot) |
| `Свежие новости`  | The most recent articles parsed from local websites                                  |
| `Личность дня`    | The most mentioned person in the media (extracted with NER)                          |
| `Слово дня`       | The most frequently used word in the articles                                        |
### Dependencies
```
# Data scraping
beautifulsoup4==4.14.3
lxml==5.3.2
requests==2.33.1

# Text processing and inference
pymorphy3==2.0.6
pymorphy3-dicts-ru==2.4.417150.4580142
nltk==3.9.4
torch==2.12.0
transformers==5.9.0

# Statistic and visualisation
matplotlib==3.10.9
seaborn==0.13.2
squarify==0.4.4

# Bot api
pyTelegramBotAPI==4.34.0

# Configuration
environs==15.0.1
```
### Setup and Start Project
First, you need to get your `API_TOKEN` using [@BotFather](https://t.me/BotFather) and the `HF_TOKEN` from [HuggingFace](https://huggingface.co/) website.

1. Clone the repo
```bash
git clone https://github.com/notBlueSpaceThinker/tg-news-digest
cd tg-news-digest
```
2. Create .env file
```bash
echo "API_TOKEN=your_bot_token" > .env
echo "HF_TOKEN=your_huggingface_token" >> .env
```
3. Create venv and download requirements
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

*And now you're good to go...*
To lauch bot simply print:
```bash
python main.py
```
### Project architecture
```
.
├── api/                        # Api for Telegram bot
│   ├── __init__.py
│   └── bot.py                  # Main logic and bot handlers
├── assets/                     # Project assets (fonts, images, etc.)
├── data/                       # Collected and processed data
│   └── YYYY-MM-DD/             # Data grouped by date
│       ├── cleaned/            # Cleaned txt
│       ├── lemmatized/         # Lemmatized txt
│       ├── meta/               # Articles metadata
│       ├── ner/                # Ner entities extracted
│       ├── raw/                # Raw txts
│       ├── stats/              # Current day statistics
│       ├── zero-shot/          # Zero-shot topic classification 
│       └── hashed_urls.json    # Processed links
├── pipeline/                   # Pipeline for data extraction and visualisation
│   ├── inference/              # NLP pipeline
│   │   ├── __init__.py
│   │   ├── inference.py        # Zero-Shot and NER inference
│   │   └── models_config.json  # Models configuration
│   ├── preprocessing/          # Text preprocessing pipeline
│   │   ├── __init__.py
│   │   └── preprocessing.py    # Text cleaning, lemmatization and etc.
│   ├── scraping/               # Scraping pipeline
│   │   ├── __init__.py
│   │   ├── core_utils.py       # Scraping utilities
│   │   ├── crawlers.py         # Crawlers
│   │   ├── parsers.py          # HTML parsers
│   │   └── scraper_config.json # Config for requesting and parsing
│   ├── stats_visualisation/    # Graphic and analytics
│   │   ├── __init__.py
│   │   ├── statistic.py        # Statistics calculation and aggregation
│   │   └── visualizer.py       # Graphs generation
│   ├── __init__.py
│   └── pipeline.py             # Pipeline orchestration
├── utils/                      # Useful functions
│   ├── __init__.py
│   ├── image.py                # Image processing and generating
│   └── io.py                   # Loading and saving files
├── .env                        # Tokens
├── config.py                   # Project configuration (tokens, paths, etc.)
└── main.py                     # Project entrypoint
```
