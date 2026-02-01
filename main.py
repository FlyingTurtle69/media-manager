#!/usr/bin/env python3
"""Script to organise TV shows and movies into proper directories using TMDB data.

Usage:
    main.py <tv|movie> <name> [OPTIONS]

Options:
  --source: The path to the original folder or file
  --season: The season number to copy to
  --episode: The specific episode number to copy to

Example:
    main.py tv "Violet Evergarden"
    main.py movie "Grave of the Fireflies" --source "./高畑勲監督作品集.Isao.Takahata.Collection.BluRay.1080p.HEVC.10bit.DTS.GOA/火垂るの墓.Grave.of.the.Fireflies.1988.BluRay.1080p.HEVC.10bit.DTS.GOA.mkv"
"""

import re
import shutil
from os import listdir
from os.path import isdir, isfile
from pathlib import Path
from sys import argv
from search import search_media, SearchType
from utils import get_env

MOVIE_PATH = get_env("MOVIE_PATH")
TV_PATH = get_env("TV_PATH")
DOWNLOADS_PATH = get_env("DOWNLOADS_PATH")


def find_source(name: str, media_type: SearchType, folder=DOWNLOADS_PATH) -> str:
    files = listdir(folder)

    if len(files) == 1:
        return f"{folder}/{files[0]}"

    for file in files:
        if (
            name.lower() in file.lower()
            or name.lower().replace(" ", ".") in file.lower()
        ):
            if media_type == "movie" and isdir(f"{folder}/{file}"):
                return find_source(name, media_type, f"{folder}/{file}")
            return f"{folder}/{file}"

    exit(1)


def episode_path(
    source: str, dest_folder: str, media_title: str, season: int, episode: int
) -> tuple[str, str]:
    suffix = source.rsplit(".", 1)[1]
    return (
        source,
        f"{dest_folder}/{media_title} S{season:02}E{episode:02}.{suffix}",
    )


def folder_episodes(
    source_folder: str, dest_folder: str, media_title: str, season: int
) -> list[tuple[str, str]]:
    files = listdir(source_folder)
    from_to = []
    regex = re.compile(r"(?:E|\[)(\d{2})\]?")
    for file in files:
        match = regex.search(file)
        if match:
            episode = int(match.group(1))
            path = episode_path(
                f"{source_folder}/{file}",
                dest_folder,
                media_title,
                season,
                episode,
            )
            from_to.append((episode, path))
    from_to.sort()
    return [ft for _, ft in from_to]


def main():
    if len(argv) < 3:
        print(__doc__)
        exit(1)

    if argv[1] not in ["movie", "tv"]:
        print(f"Invalid search type: {argv[1]}")
        exit(1)
    media_type: SearchType = argv[1]  # type: ignore

    name = argv[2]
    source = None
    season = 1
    episode = None

    for i in range(3, len(argv), 2):
        if argv[i] == "--source":
            source = argv[i + 1]
        elif argv[i] == "--season":
            season = int(argv[i + 1])
        elif argv[i] == "--episode":
            episode = int(argv[i + 1])

    if source is None:
        source = find_source(name, media_type)

    media = search_media(name, media_type)
    print()

    if media_type == "movie":
        suffix = source.rsplit(".", 1)[1]
        from_to = [
            (
                source,
                f"{MOVIE_PATH}/{media.title} ({media.release_date[:4]}) [tmdbid-{media.id}].{suffix}",
            )
        ]
    else:
        dest_path = (
            f"{TV_PATH}/{media.title} ({media.release_date[:4]}) [tmdbid-{media.id}]"
        )
        if not isdir(dest_path):
            print(f"This directory will be created: {dest_path}")
        dest_path += f"/Season {season:02}"
        if not isdir(dest_path):
            print(f"This directory will be created: {dest_path}")

        if episode is not None:
            from_to = [episode_path(source, dest_path, media.title, season, episode)]
        else:
            from_to = folder_episodes(source, dest_path, media.title, season)

    print(f"{len(from_to)} files to be copied:")
    for fro, to in from_to:
        extra = ""
        if isfile(to):
            extra = " (overwriting)"
        print(f"{fro} -> {to}{extra}")

    if input("\nContinue? (y/n) ").lower() == "y":
        for fro, to in from_to:
            src = Path(fro)
            dst = Path(to)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print("Finished.")
    else:
        print("Aborted.")
        exit(2)


if __name__ == "__main__":
    main()
