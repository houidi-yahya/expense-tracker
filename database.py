import os 
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()


def get_env(name):
    try:
        return os.environ[name]
    except KeyError:
        raise RuntimeError(f"{name} is missing")

host=get_env("DB_HOST")
password=get_env("DB_PASSWORD")
name=get_env("DB_NAME")
user=get_env("DB_USER")



def get_db():
    with psycopg.connect(
        dbname=name,
        user=user,
        password=password,
        host=host,
        port=5432,
        row_factory=dict_row,
    ) as conn:
        yield conn

