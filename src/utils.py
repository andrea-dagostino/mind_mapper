import wave
import contextlib
from pydub import AudioSegment

import hashlib
import datetime

from src import logger

logger = logger.get_console_logger("utils")


def compute_cost_of_audio_track(audio_track_file_path: str):
    file_extension = audio_track_file_path.split(".")[-1].lower()
    duration_seconds = 0
    if file_extension == "wav":
        with contextlib.closing(wave.open(audio_track_file_path, "rb")) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration_seconds = frames / float(rate)
    elif file_extension == "mp3":
        audio = AudioSegment.from_mp3(audio_track_file_path)
        duration_seconds = len(audio) / 1000.0  # pydub returns duration in milliseconds
    else:
        logger.error(f"Unsupported file format: {file_extension}")
        return

    audio_duration_in_minutes = duration_seconds / 60
    cost = round(audio_duration_in_minutes, 2) * 0.006  # default price of whisper model
    logger.info(f"Cost to convert {audio_track_file_path} is ${cost:.2f}")
    return cost


def hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def convert_timestamp_to_datetime(timestamp: str) -> str:
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
