import requests
import json
import re
import sys
import pathlib
import yt_dlp

ROOT_URL = "https://play.mathadventure.hs-bochum.de"
ROOT_MAP = f"{ROOT_URL}/_/global/mathadventure.hs-bochum.de/map/maps/lobby.tmj"

OUT_DIR = pathlib.Path(__file__).parent.parent / "out"

crawled = set()


# we need the v= part of the url
# https://mathadventure.hs-bochum.de/media/?v=//mathadventure.hs-bochum.de/media/streams/Vorlesungsvideos/U_Aussagenlogik_A5.mp4.m3u8
def extract_media_urls(map_info_txt):
    video_urls = re.findall(
        r"=(https:)?(\/\/mathadventure.hs-bochum.de\/media\/[^\"]*)",
        map_info_txt,
    )

    for video_url in video_urls:
        yield f"https:{video_url[1]}"


def get_map_info(play_uri: str) -> dict:
    # url encode the play_uri
    url_encoded_play_uri = requests.utils.quote(play_uri)

    response = requests.get(
        f"https://play.mathadventure.hs-bochum.de/map?playUri={url_encoded_play_uri}"
    )
    response.raise_for_status()

    map_url = response.json()["mapUrl"]

    res = requests.get(map_url)

    return res.json()


def crawler(map_link: str):
    # replace umlauts \u00fc -> ü etc.
    map_link = map_link.encode("utf-8").decode("unicode_escape")

    print("Crawling", map_link, file=sys.stderr)

    try:
        if map_link in crawled:
            return

        crawled.add(map_link)

        map_info = get_map_info(map_link)

        map_info_txt = json.dumps(map_info)
        # last slash of url
        map_name = map_link.split("/")[-1]

        map_dir = OUT_DIR / map_name.split(".")[0]
        map_dir.mkdir(exist_ok=True, parents=True)

        map_links = re.findall(
            r"/_/global/mathadventure.hs-bochum.de/map/maps/[^\"]*\.tmj",
            map_info_txt,
        )

        for map_link in map_links:
            crawler(f"{ROOT_URL}{map_link}")

        for media_url in extract_media_urls(map_info_txt):
            # remove umlauts \u00fc -> ü etc.
            media_url = media_url.encode("utf-8").decode("unicode_escape")

            media_name = media_url.split("/")[-1]
            media_path = map_dir / media_name

            if media_path.exists():
                continue

            is_video = media_name.endswith(".m3u8")

            if is_video:
                media_path = media_path.with_suffix(".mp4")

                if media_path.exists():
                    continue

                yt_ops = {
                    "noplaylist": True,
                    "outtmpl": media_path.as_posix(),
                }

                with yt_dlp.YoutubeDL(yt_ops) as yt:
                    yt.download([media_url])
            else:
                res = requests.get(media_url)
                res.raise_for_status()

                with open(media_path, "wb") as f:
                    f.write(res.content)

    except Exception as e:
        print(f"Error while crawling {map_link}: {e}", file=sys.stderr)


def main():
    crawler(ROOT_MAP)
