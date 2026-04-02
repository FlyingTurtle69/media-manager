#!/usr/bin/env python3
"""Script to organise TV shows and movies into proper directories using TMDB data.

Usage:
    main.py <tv|movie> <name> [OPTIONS]

Options:
  --source: The path to the original folder or file
  --season: The season number to copy to
  --episode: The specific episode number to copy to
  --shift: An integer to add to episode numbers (default: 0)

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
from search import Media, search_media, SearchType
from utils import get_env
from tqdm import tqdm

MOVIE_PATH = get_env("MOVIE_PATH")
TV_PATH = get_env("TV_PATH")
DOWNLOADS_PATH = get_env("DOWNLOADS_PATH")

SUBTITLE_SUFFIXES = ["srt", "ass"]
LANGUAGE_SUFFIX = "ja"

REPLACE_CHAR = ""


def find_match(name: str, folder: str) -> str | None:
    for file in listdir(folder):
        if (
            name.lower() in file.lower()
            or name.lower().replace(" ", ".") in file.lower()
        ):
            return file
    return None


def find_source(name: str, media_type: SearchType, folder=DOWNLOADS_PATH) -> str:
    files = listdir(folder)

    if len(files) == 1:
        return f"{folder}/{files[0]}"

    match = find_match(name, folder)
    if match:
        if media_type == "movie" and isdir(f"{folder}/{match}"):
            return find_source(name, media_type, f"{folder}/{match}")
        return f"{folder}/{match}"

    print("Source not found")
    exit(1)


def make_suffix(source: str) -> str:
    suffix = source.rsplit(".", 1)[1]
    if suffix in SUBTITLE_SUFFIXES:
        return f"{LANGUAGE_SUFFIX}.{suffix}"
    return suffix


def episode_path(
    source: str, dest_folder: str, media_title: str, season: int, episode: int
) -> tuple[str, str]:
    suffix = make_suffix(source)
    return (
        source,
        f"{dest_folder}/{media_title} S{season:02}E{episode:02}.{suffix}",
    )


def parse_season(path: Path, default_season: int) -> tuple[int, bool]:
    search_str = f"{path.parent.name} {path.name}".lower()
    
    if re.search(r'\b(ova|special|sp|ncop|nced)(?:\d+|\b)', search_str):
        return 0, True
        
    season_match = re.search(r'\b(?:season\s*|s)(\d+)', search_str)
    if season_match:
        return int(season_match.group(1)), False
        
    return default_season, False


def folder_episodes(
    source_folder: str, dest_folder_base: str, media_title: str, default_season: int, shift: int = 0
) -> list[tuple[str, str]]:
    source_path = Path(source_folder)
    from_to = []
    regex = re.compile(r"(?:EP(\d{2})|E(\d{2})|\[(\d{2})\]| (\d{2}) )", re.IGNORECASE)
    
    # Sort files alphabetically to ensure consistent order, especially for interactive prompts
    paths = sorted(list(source_path.rglob("*")))
    
    for path in paths:
        if not path.is_file():
            continue
            
        season, is_special = parse_season(path, default_season)
        
        episode = None
        if is_special:
            while True:
                user_input = input(f"Special found: {path.name}\nEnter episode number (or 'skip' to ignore): ")
                if user_input.lower() == 'skip':
                    break
                try:
                    episode = int(user_input)
                    break
                except ValueError:
                    print("Please enter a valid integer.")
            if episode is None:
                continue
        else:
            match = regex.search(path.name)
            if match:
                episode = int(next(g for g in match.groups() if g is not None)) + shift
            else:
                continue
                
        dest_folder = f"{dest_folder_base}/Season {season:02}"
        _, to_path = episode_path(str(path), dest_folder, media_title, season, episode)
        from_to.append((season, episode, str(path), to_path))
        
    from_to.sort(key=lambda x: (x[0], x[1]))
    return [(ft[2], ft[3]) for ft in from_to]


def get_media(name: str, media_type: SearchType) -> Media:
    """Try to get media information locally first, then fall back to searching TMDB."""
    if media_type == "tv":
        match = find_match(name, TV_PATH)
        if match:
            parsed = re.match(r"(.+?)\s+\((\d{4})\)\s+\[tmdbid-(\d+)\]", match)
            if parsed:
                title, year, tmdbid = parsed.groups()
                print(f"Found locally: {match}")
                return Media(id=int(tmdbid), title=title, release_date=f"{year}-01-01")
    return search_media(name, media_type)


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
    shift = 0

    for i in range(3, len(argv), 2):
        if argv[i] == "--source":
            source = argv[i + 1]
        elif argv[i] == "--season":
            season = int(argv[i + 1])
        elif argv[i] == "--episode":
            episode = int(argv[i + 1])
        elif argv[i] == "--shift":
            shift = int(argv[i + 1])
        else:
            print(f"Unknown option: {argv[i]}")
            exit(1)

    if source is None:
        source = find_source(name, media_type)
        print("Source: ", source)

    media = get_media(name, media_type)

    # Handle : since it's not allowed in file names
    media.title = media.title.replace(":", REPLACE_CHAR)

    print()

    if media_type == "movie":
        suffix = make_suffix(source)
        from_to = [
            (
                source,
                f"{MOVIE_PATH}/{media.title} ({media.release_date[:4]}) [tmdbid-{media.id}].{suffix}",
            )
        ]
    else:
        dest_path_base = (
            f"{TV_PATH}/{media.title} ({media.release_date[:4]}) [tmdbid-{media.id}]"
        )
        if not isdir(dest_path_base):
            print(f"This directory will be created: {dest_path_base}")

        if episode is not None:
            dest_path = f"{dest_path_base}/Season {season:02}"
            if not isdir(dest_path):
                print(f"This directory will be created: {dest_path}")
            from_to = [episode_path(source, dest_path, media.title, season, episode)]
        else:
            from_to = folder_episodes(source, dest_path_base, media.title, season, shift)

    print(f"{len(from_to)} files to be copied:")
    for fro, to in from_to:
        extra = ""
        if isfile(to):
            extra = " (overwriting)"
        print(f"{fro} -> {to}{extra}")

    if input("\nContinue? (y/n) ").lower() == "y":
        for fro, to in tqdm(from_to):
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
