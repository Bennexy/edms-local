from os import environ as env
from pathlib import Path
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


DEV_MODE: bool = env.get("DEV_MODE", False)
VERSION: str = env.get("version", "0.0.1")
DATABASE_URI: str = env.get("DATABASE_URI")
SECRET_KEY: str = env.get("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("SECRET_KEY must not be none!!!")

BASE_FILE_DIR: Path = Path(env.get("BASE_FILE_DIR", "files")).absolute()
