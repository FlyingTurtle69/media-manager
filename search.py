from typing import Literal
from pydantic import BaseModel
import tmdbsimple as tmdb
from utils import get_env

tmdb.API_KEY = get_env("TMDB_API_KEY")
MOVIE_PATH = get_env("MOVIE_PATH")
TV_PATH = get_env("TV_PATH")

SearchType = Literal["movie", "tv"]

class Media(BaseModel):
    id: int
    title: str
    release_date: str

def search_media(query: str, search_type: SearchType) -> Media:
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
    return Media(**response[choice])

def search_to_destination(query: str, search_type: SearchType) -> str:
    media = search_media(query, search_type)
    folder = MOVIE_PATH if search_type == "movie" else TV_PATH
    return f"{folder}/{media.title} ({media.release_date[:4]}) [tmdbid-{media.id}]"
