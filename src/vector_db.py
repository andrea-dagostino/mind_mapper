from src.logger import get_console_logger

import os
from dotenv import load_dotenv
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from upstash_vector import Index, Vector
from tqdm import trange, tqdm
import random

# Load environment variables
load_dotenv()

# Constants
OPENAI_KEY = os.getenv("OPENAI_KEY")
UPSTASH_ENDPOINT = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
MODEL = "text-embedding-ada-002"

# Global objects
ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")
logger = get_console_logger("vector_db")
openai_client = OpenAI(api_key=OPENAI_KEY)
index = Index(url=UPSTASH_ENDPOINT, token=UPSTASH_TOKEN)  # Moved here for global access


def token_len(text):
    """Calculate the token length of a given text."""
    return len(ENCODER.encode(text))


def get_embeddings(chunks, model=MODEL):
    """Get embeddings for a list of text chunks."""
    chunks = [c.replace("\n", " ") for c in chunks]
    res = openai_client.embeddings.create(input=chunks, model=model).data
    return [r.embedding for r in res]


def get_embedding(text, model=MODEL):
    """Get embedding for a single text."""
    # text = text.replace("\n", " ")
    return get_embeddings([text], model)[0]


def query(question, system_prompt="", top_n=1):
    """Ask a question and print the response based on similar vectors found."""
    logger.info("Creating vector for question...")
    question_embedding = get_embedding(question)
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


def add_chunks_to_vector_db(chunks, metadata):
    """Embed text chunks and return a list of Vector objects."""
    for chunk in chunks:
        random_id = random.randint(0, 1000000)
        metadata["text"] = chunk
        vec = Vector(
            id=f"chunk-{random_id}", vector=get_embedding(chunk), metadata=metadata
        )
        index.upsert(vectors=[vec])
        logger.info(f"Added chunk to vector db: {chunk}")

    # vectors = []
    # batch_count = 10
    # for i in trange(0, len(chunks), batch_count):
    #     batch = chunks[i : i + batch_count]
    #     embeddings = get_embeddings(batch)
    #     for i, chunk in enumerate(batch):
    #         random_id = random.randint(0, 1000000)
    #         metadata["text"] = chunk
    #         vec = Vector(id=f"chunk-{random_id}", vector=embeddings[i], metadata=metadata)
    #         vectors.append(vec)
    # return vectors


def fetch_by_source_hash_id(source_hash_id: str, max_results=10000):
    ids = []
    for i in tqdm(range(0, max_results, 1000)):
        search = index.range(
            cursor=str(i), limit=1000, include_vectors=False, include_metadata=True
        ).vectors
        for result in search:
            if result.metadata["source_hash_id"] == source_hash_id:
                ids.append(result.id)
    return ids


def fetch_all():
    return index.range(
        cursor="0", limit=1000, include_vectors=False, include_metadata=True
    ).vectors


def main():
    """Main function to process file data and ask a question."""
    # filedata = "..."  # Placeholder for actual file data
    # chunks = create_chunks(filedata)
    # vectors = embed_chunks(chunks)
    # index.upsert(vectors)
    # ask_question("What is this file about?")
    # fetch_by_source_hash_id({"source_hash_id": "fad5473682d2aa9ba3b4cbc2bc7fb090"})


if __name__ == "__main__":
    main()
