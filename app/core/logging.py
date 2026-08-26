import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")


def setup_logging():
    """
    Configure logging for the application.
    """

    log_level = logging.DEBUG if APP_ENV == "development" else logging.INFO

    dev_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    prod_format = (
        '{"time":"%(asctime)s",'
        '"level":"%(levelname)s",'
        '"module":"%(namse)s",'
        '"message":"%(message)s"}'
    )

    log_format = (
        dev_format
        if APP_ENV == "development"
        else prod_format
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


def get_logger(name: str):
    return logging.getLogger(name)