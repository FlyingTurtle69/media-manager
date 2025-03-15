#!/usr/bin/env python3
"""
Script to bulk move / symlink files from one directory to another.

Usage:
    move.py [--move] <source prefix> <destination> [new suffix] [season]

Options:
    --move Move files instead of symlinking them.
    <source prefix> The path up until the number of the file.
    <destination> The directory to move the files to. The new files will be named the name of the directory
                  without the (year) and adding S01E and the episode number.
    [new suffix] The new file extension to use instead of the old one. If not given, the old one will be used.
    [season] The season number to use. If not given, the default is 1.

Example:
    move.py "Downloads/Kamen Rider OOO/[OZC-Live]Kamen Rider OOO BD Box E" "テレビ番組/仮面ライダーオーズ (2010)"
    move.py --move "Downloads/Kamen Rider OOO/Kamen Rider OOO 0" "テレビ番組/仮面ライダーオーズ (2010)" "ja.srt"

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


def new_path(f: str, dest: str, plen: int, suffix: str, season: int) -> str:
    if suffix == "":
        suffix = f.rsplit(".", 1)[1]
    num = f[plen:plen + 2]
    name = dest.rsplit("/", 1)[1].rsplit("(", 1)[0]
    s = f"{season:02}"
    season_folder = f"Season {s}/"
    return f"{dest}/{season_folder}{name}S{s}E{num}.{suffix}"


def main():
    if len(argv) < 3:
        print(__doc__)
        exit(1)

    if argv[1] == '--move':
        argv.pop(1)
        mv = move
    else:
        mv = symlink

    dir, prefix = argv[1].rsplit('/', 1)
    plen = len(prefix)

    dest = argv[2]
    if dest[-1] == '/':
        dest = dest[:-1]

    suffix = ""
    if len(argv) > 3:
        suffix = argv[3]

    season = int(argv[4]) if len(argv) > 4 else 1

    files = [(dir + "/" + f, new_path(f, dest, plen, suffix, season))
             for f in listdir(dir)
             if f.startswith(prefix)]

    if mv is symlink:
        if dir[0] != "/":
            print(
                "WARNING: Source is not an absolute path. This will likely not work."
            )
        print("These symlinks will be created:")
    else:
        print("These files will be MOVED:")

    for f, p in files:
        extra = ""
        if isfile(p):
            extra = " (overwriting)"
        print(f"{f} -> {p}{extra}")

    if not isdir(dest):
        print(f"This directory will be created: {dest}")

    if input("Continue? (y/n) ").lower() == 'y':
        if not isdir(dest):
            mkdir(dest)
        for f, p in files:
            mv(f, p)
        print("Finished.")
    else:
        print("Aborted.")
        exit(2)


if __name__ == '__main__':
    main()
