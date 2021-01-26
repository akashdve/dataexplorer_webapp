import os

from py_dotenv import read_dotenv

read_dotenv(".env")


class Config:
    VERSION = "0.1.1"
    TMP_DIR = os.getenv("TEMP_DIR")
