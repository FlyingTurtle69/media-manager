from os import getenv
from sys import exit
from dotenv import load_dotenv
load_dotenv()

def get_env(var: str) -> str:
    result = getenv(var)
    if result is None:
        print("Missing environment variable:", var)
        exit(1)
    return result
