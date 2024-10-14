# Mathadventure Crawler HS Bochum

Simple crawler to download all videos and documents out of Mathadventure.
I really can not be bothered to walk through a game to get to the content I want to see.
So I wrote this script to do it for me.

## Usage

This project uses [poetry](https://python-poetry.org/) for dependency management.
To install the dependencies run:

```bash
poetry install
```

No configuration is needed. Just run the script with:

```bash
poetry run python main.py
```

The downloaded files will be saved in the `out` folder.
