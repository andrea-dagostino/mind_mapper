from src.logger import get_console_logger

import os
from dotenv import load_dotenv
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from upstash_vector import Vector
from tqdm import trange, tqdm
import random


MODEL = "text-embedding-ada-002"

# Global objects
ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")
logger = get_console_logger("vector_db")


def token_len(text):
    """Calculate the token length of a given text."""
    return len(ENCODER.encode(text))


def get_embeddings(openai_client, chunks, model=MODEL):
    """Get embeddings for a list of text chunks."""
    chunks = [c.replace("\n", " ") for c in chunks]
    res = openai_client.embeddings.create(input=chunks, model=model).data
    return [r.embedding for r in res]


def get_embedding(openai_client, text, model=MODEL):
    """Get embedding for a single text."""
    # text = text.replace("\n", " ")
    return get_embeddings(openai_client, [text], model)[0]


def query_vector_db(index, openai_client, question, system_prompt="", top_n=1):
    """Ask a question and print the response based on similar vectors found."""
    logger.info("Creating vector for question...")
    question_embedding = get_embedding(openai_client, question)
    logger.info("Querying vector database...")
    res = index.query(vector=question_embedding, top_k=top_n, include_metadata=True)
    context = "\n-".join([r.metadata["text"] for r in res])
    logger.info(f"Context returned. Length: {len(context)} characters.")
    return context


def create_chunks(text, chunk_size=150, chunk_overlap=20):
    """Create text chunks based on specified size and overlap."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=token_len,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_text(text)


def add_chunks_to_vector_db(index, chunks, metadata):
    """Embed text chunks and return a list of Vector objects."""
    for chunk in chunks:
        random_id = random.randint(0, 1000000)
        metadata["text"] = chunk
        vec = Vector(
            id=f"chunk-{random_id}", vector=get_embedding(chunk), metadata=metadata
        )
        index.upsert(vectors=[vec])
        logger.info(f"Added chunk to vector db: {chunk}")


def fetch_by_source_hash_id(index, source_hash_id: str, max_results=10000):
    ids = []
    for i in tqdm(range(0, max_results, 1000)):
        search = index.range(
            cursor=str(i), limit=1000, include_vectors=False, include_metadata=True
        ).vectors
        for result in search:
            if result.metadata["source_hash_id"] == source_hash_id:
                ids.append(result.id)
    return ids


def fetch_all(index):
    return index.range(
        cursor="0", limit=1000, include_vectors=False, include_metadata=True
    ).vectors
