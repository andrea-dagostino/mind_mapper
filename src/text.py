from src.logger import get_console_logger
from src.db import add_one
from src.utils import hash_text
from src.schema import FileType

import typer

logger = get_console_logger("text")


def extract_text_from_file(file_path: str) -> str:
    logger.info(f"Extracting text from file: {file_path}")
    with open(file_path, "r") as file:
        return file.read()
    # TODO: add .csv support


def save_text(text: str) -> None:
    add_one(
        {
            "file_type": FileType.TEXT,
            "hash_id": hash_text(text),
            "text": text,
        }
    )


def extract_text_and_save(file_path: str) -> None:
    text = extract_text_from_file(file_path)
    save_text(text)


if __name__ == "__main__":
    typer.run(extract_text_and_save)
