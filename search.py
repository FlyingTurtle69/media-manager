from typing import Literal
from dotenv import load_dotenv
from os import getenv
import tmdbsimple as tmdb

load_dotenv()
tmdb.API_KEY = getenv("TMDB_API_KEY")
MOVIE_PATH = getenv("MOVIE_PATH")
TV_PATH = getenv("TV_PATH")

SearchType = Literal["movie", "tv"]


def search_to_destination(query: str, search_type: SearchType) -> str:
    search = tmdb.Search()
    if search_type == "movie":
        response = search.movie(query=query)["results"]
    else:
        response = search.tv(query=query)["results"]
        for show in response:
            show["release_date"] = show.pop("first_air_date")
            show["title"] = show.pop("name")

    for i, movie in enumerate(response):
        print(f"{i}: {movie['title']} ({movie['release_date'][:4]})")
    choice = int(input("Enter number: "))
    media = response[choice]

    folder = MOVIE_PATH if search_type == "movie" else TV_PATH
    return f"{folder}/{media["title"]} ({media["release_date"][:4]}) [tmdbid-{media['id']}]"
