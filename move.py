#!/usr/bin/env python3
"""
Script to bulk move / hardlink files from one directory to another.

Usage:
    move.py [--move] <source prefix> <destination> [count] [new suffix]

Options:
    --move Move files instead of hardlinking them.
    <source prefix> The path up until the number of the file.
    <destination> The directory to move the files to. The new files will be named the name of the directory
                  without the (year) and adding S01E and the episode number.
    [count] The number of files to move as a range start-end. If a number is given instead, it will be 1-end.
            It's assumed that the numbers are two digit such as 05 and 12.
    [new suffix] The new file extension to use instead of the old one. If not given, the old one will be used.

Example:
    move.py "Downloads/Kamen Rider OOO/[OZC-Live]Kamen Rider OOO BD Box E" 46 "テレビ番組/仮面ライダーオーズ (2010)"
    move.py --move "Downloads/Kamen Rider OOO/Kamen Rider OOO 0" 16-48 "テレビ番組/仮面ライダーオーズ (2010)" "ja.srt"

These examples (only using E16) result in a structure like:
    Downloads/
        [OZC-Live]Kamen Rider OOO BD Box E16 'A Conclusion, a Greed, and a New Rider' [720p].mkv
    テレビ番組/
        仮面ライダーオーズ (2010)/
            仮面ライダーオーズ S01E16.mkv
            仮面ライダーオーズ S01E16.ja.srt
"""

from sys import argv, exit
from os import link, rename, listdir


def main():
    if len(argv) < 3:
        print(__doc__)
        exit(1)

    if argv[1] == '--move':
        argv.pop(1)
        move = rename
    else:
        move = link

    dir, prefix = argv[1].rsplit('/', 1)
    plen = len(prefix)

    froms = [
        f for f in listdir(dir)
        if f.startswith(prefix) and int(f[plen:plen + 2])
    ]


if __name__ == '__main__':
    main()
