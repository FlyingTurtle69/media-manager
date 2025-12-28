#!/usr/bin/env python3
"""
Script to bulk move / symlink files from one directory to another.

Usage:
    move.py [--move] <source prefix> <destination> [--suffix suffix] [--season season] [--ignore words] [--shift shift] [--search type]

Options:
    --move Move files instead of symlinking them.
    <source prefix> The path up until the number of the file.
    <destination> The directory to move the files to. The new files will be named the name of the directory
                  without the (year) and adding S01E and the episode number.
    [suffix] The new file extension to use instead of the old one. If not given, the old one will be used.
    [season] The season number to use. If not given, the default is 1. If "none" is given, no season dir will be created.
    [words] A comma-separated list of words. Any files that contain any of these words will be ignored.
    [shift] An integer to add to the episode numbers. Can be negative.
    [type] Either "movie" or "tv". If given, the destination will be searched for using TMDB.

Example:
    move.py "Downloads/Kamen Rider OOO/[OZC-Live]Kamen Rider OOO BD Box E" "テレビ番組/仮面ライダーオーズ (2010)"
    move.py --move "Downloads/Kamen Rider OOO/Kamen Rider OOO 0" "テレビ番組/仮面ライダーオーズ (2010)" --suffix "ja.srt"

These examples (only using E16) result in a structure like:
    Downloads/
        [OZC-Live]Kamen Rider OOO BD Box E16 'A Conclusion, a Greed, and a New Rider' [720p].mkv
    テレビ番組/
        仮面ライダーオーズ (2010)/
            Season 01/
                仮面ライダーオーズ S01E16.mkv
                仮面ライダーオーズ S01E16.ja.srt
"""

from sys import argv, exit
from os import symlink, listdir, mkdir
from os.path import isfile, isdir
from shutil import move
from search import search_to_destination


def season_path(dest: str, season: int) -> str:
    if season == -1:
        return dest
    return f"{dest}/Season {season:02}"


def new_path(f: str, dest: str, plen: int, suffix: str, season: int, shift: int) -> str:
    if suffix == "":
        suffix = f.rsplit(".", 1)[1]
    num = f"{int(f[plen : plen + 2]) + shift:02}"
    name = dest.rsplit("/", 1)[1].rsplit("(", 1)[0]
    s = f"{abs(season):02}"
    return f"{season_path(dest, season)}/{name}S{s}E{num}.{suffix}"


def main():
    if len(argv) < 3:
        print(__doc__)
        exit(1)

    if argv[1] == "--move":
        argv.pop(1)
        mv = move
    else:
        mv = symlink

    destination = argv[1]

    dest = argv[2]
    if dest[-1] == "/":
        dest = dest[:-1]

    suffix = ""
    season = 1
    ignore = []
    shift = 0

    for i in range(3, len(argv), 2):
        if argv[i] == "--suffix":
            suffix = argv[i + 1]
        elif argv[i] == "--season":
            n = argv[i + 1]
            season = -1 if n == "none" else int(n)
        elif argv[i] == "--ignore":
            ignore = argv[i + 1].split(",")
        elif argv[i] == "--shift":
            shift = int(argv[i + 1])
            if shift != 0:
                print(f"Shifting episode numbers by {shift}.")
        elif argv[i] == "--search":
            search_type = argv[i + 1]
            if search_type not in ["movie", "tv"]:
                print(f"Invalid search type: {search_type}")
                exit(1)
            destination = search_to_destination(dest, search_type)  # type: ignore
        else:
            print(f"Unknown argument: {argv[i]}")
            exit(1)

    dir, prefix = destination.rsplit("/", 1)
    plen = len(prefix)

    files = [
        (dir + "/" + f, new_path(f, dest, plen, suffix, season, shift))
        for f in listdir(dir)
        if all(i not in f for i in ignore) and f.startswith(prefix)
    ]

    if mv is symlink:
        if dir[0] != "/":
            print("WARNING: Source is not an absolute path. This will likely not work.")
        print(f"{len(files)} symlinks will be created:")
    else:
        print(f"{len(files)} files will be MOVED:")

    for f, p in files:
        extra = ""
        if isfile(p):
            extra = " (overwriting)"
        print(f"{f} -> {p}{extra}")

    if not isdir(dest):
        print(f"This directory will be created: {dest}")
    if not isdir(season_path(dest, season)):
        print(f"This directory will be created: {season_path(dest, season)}")

    if input("Continue? (y/n) ").lower() == "y":
        if not isdir(dest):
            mkdir(dest)
        if not isdir(season_path(dest, season)):
            mkdir(season_path(dest, season))
        for f, p in files:
            mv(f, p)
        print("Finished.")
    else:
        print("Aborted.")
        exit(2)


if __name__ == "__main__":
    main()
