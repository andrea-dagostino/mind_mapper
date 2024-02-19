from src.logger import get_console_logger
from src.db import add_one
from src.utils import hash_text
from src.schema import FileType

logger = get_console_logger("whisper")


def create_transcript(openai_client, file_path: str) -> None:
    audio_file = open(file_path, "rb")
    logger.info(f"Creating transcript for {file_path}")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcript.text


def create_transcript_and_save(openai_client, file_path: str) -> None:
    transcript = create_transcript(openai_client, file_path)
    add_one(
        {
            "file_type": FileType.AUDIO,
            "hash_id": hash_text(transcript),
            "text": transcript,
        }
    )
