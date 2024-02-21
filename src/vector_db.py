from src.logger import get_console_logger

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from upstash_vector import Vector
from tqdm import tqdm
import random

logger = get_console_logger("vector_db")

MODEL = "text-embedding-ada-002"
ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")


def token_len(text):
    """Calculate the token length of a given text.

    Args:
        text (str): The text to calculate the token length for.

    Returns:
        int: The number of tokens in the text.
    """
    return len(ENCODER.encode(text))


def get_embeddings(openai_client, chunks, model=MODEL):
    """Get embeddings for a list of text chunks using the specified model.

    Args:
        openai_client: The OpenAI client instance to use for generating embeddings.
        chunks (list of str): The text chunks to embed.
        model (str): The model identifier to use for embedding.

    Returns:
        list of list of float: A list of embeddings, each corresponding to a chunk.
    """
    chunks = [c.replace("\n", " ") for c in chunks]
    res = openai_client.embeddings.create(input=chunks, model=model).data
    return [r.embedding for r in res]


def get_embedding(openai_client, text, model=MODEL):
    """Get embedding for a single text using the specified model.

    Args:
        openai_client: The OpenAI client instance to use for generating the embedding.
        text (str): The text to embed.
        model (str): The model identifier to use for embedding.

    Returns:
        list of float: The embedding of the given text.
    """
    # text = text.replace("\n", " ")
    return get_embeddings(openai_client, [text], model)[0]


def query_vector_db(index, openai_client, question, top_n=1):
    """Query the vector database for similar vectors to the given question.

    Args:
        index: The vector database index to query.
        openai_client: The OpenAI client instance to use for generating the question embedding.
        question (str): The question to query the vector database with.
        system_prompt (str, optional): An additional prompt to provide context for the question. Defaults to an empty string.
        top_n (int, optional): The number of top similar vectors to return. Defaults to 1.

    Returns:
        str: A string containing the concatenated texts of the top similar vectors.
    """
    logger.info("Creating vector for question...")
    question_embedding = get_embedding(openai_client, question)
    logger.info("Querying vector database...")
    res = index.query(vector=question_embedding, top_k=top_n, include_metadata=True)
    context = "\n-".join([r.metadata["text"] for r in res])
    logger.info(f"Context returned. Length: {len(context)} characters.")
    return context


def create_chunks(text, chunk_size=150, chunk_overlap=20):
    """Create text chunks based on specified size and overlap.

    Args:
        text (str): The text to split into chunks.
        chunk_size (int, optional): The desired size of each chunk. Defaults to 150.
        chunk_overlap (int, optional): The number of overlapping characters between chunks. Defaults to 20.

    Returns:
        list of str: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=token_len,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_text(text)


def add_chunks_to_vector_db(index, chunks, metadata):
    """Embed text chunks and add them to the vector database.

    Args:
        index: The vector database index to add chunks to.
        chunks (list of str): The text chunks to embed and add.
        metadata (dict): The metadata to associate with each chunk.

    Returns:
        None
    """
    for chunk in chunks:
        random_id = random.randint(0, 1000000) # workaround while waiting for metadata search to be implemented
        metadata["text"] = chunk
        vec = Vector(
            id=f"chunk-{random_id}", vector=get_embedding(chunk), metadata=metadata
        )
        index.upsert(vectors=[vec])
        logger.info(f"Added chunk to vector db: {chunk}")


def fetch_by_source_hash_id(index, source_hash_id: str, max_results=10000):
    """Fetch vector IDs from the database by source hash ID.

    Args:
        index: The vector database index to search.
        source_hash_id (str): The source hash ID to filter the vectors by.
        max_results (int, optional): The maximum number of results to return. Defaults to 10000.

    Returns:
        list of str: A list of vector IDs that match the source hash ID.
    """
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
    """Fetch all vectors from the database.

    Args:
        index: The vector database index to fetch vectors from.

    Returns:
        list: A list of vectors from the database.
    """
    return index.range(
        cursor="0", limit=1000, include_vectors=False, include_metadata=True
    ).vectors
