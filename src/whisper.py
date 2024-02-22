from src.logger import get_console_logger

logger = get_console_logger("whisper")


def create_transcript(openai_client, file_path: str) -> None:
    audio_file = open(file_path, "rb")
    logger.info(f"Creating transcript for {file_path}")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    logger.info(f"Transcript created for {file_path}")
    return transcript.text
