from src.logger import get_console_logger
from src.llm.prompts import PROMPTS

import os


logger = get_console_logger("llm")


def extract_mind_map_data(openai_client, text: str) -> None:
    logger.info(f"Extracting mind map data from text...")
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content": PROMPTS["mind_map_of_one"]},
            {"role": "user", "content": f"{text}"},
        ],
    )
    return response.choices[0].message.content


def extract_mind_map_data_of_two(
    openai_client, source_text: str, target_text: str
) -> None:
    logger.info(f"Extracting mind map data from two texts...")
    user_prompt = PROMPTS["mind_map_of_many"].format(
        source_text=source_text, target_text=target_text
    )
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": PROMPTS["mind_map_of_many"]},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def extract_information_from_mind_map_data(openai_client, data: dict) -> None:
    logger.info(f"Extracting information from mind map data...")
    user_prompt = PROMPTS["inspector_of_mind_map"].format(mind_map_data=data)
    response = openai_client.chat.completions.create(
        model="gpt-4",
        # response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": PROMPTS["inspector_of_mind_map"]},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
