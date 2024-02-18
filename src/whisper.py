from src.logger import get_console_logger
from src.db import add_one
from src.utils import hash_text
from src.schema import FileType

import typer
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
logger = get_console_logger("whisper")
openai_client = OpenAI(api_key=OPENAI_KEY)


def create_transcript(file_path: str) -> None:
    audio_file = open(file_path, "rb")
    logger.info(f"Creating transcript for {file_path}")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcript.text


def create_transcript_and_save(file_path: str) -> None:
    transcript = create_transcript(file_path)
    add_one(
        {
            "file_type": FileType.AUDIO,
            "hash_id": hash_text(transcript),
            "text": transcript,
        }
    )


if __name__ == "__main__":
    typer.run(create_transcript_and_save)
