from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path
from typing import List

import chromadb
from chromadb.api.types import QueryResult
from openai import OpenAI

from post_extraction import read_posts

from .models import Post

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
chroma_client = chromadb.HttpClient(host="localhost", port=8000)


def get_embedding(text, model="text-embedding-embeddinggemma-300m"):
    text = text.replace("\n", " ")
    data = client.embeddings.create(input=[text], model=model).data[0]
    return data.embedding


def chunk_post(post: Post) -> List[str]:
    content = post.content
    if not content:
        return []

    return re.split(r"\n#+\s", content)


def get(query: str) -> QueryResult:
    collection = chroma_client.get_or_create_collection(name="posts")
    embedding = get_embedding(query)
    return collection.query(query_embeddings=[embedding], n_results=5)


def populate_vector_db():
    DIR = Path(__file__).parent.absolute()
    collection = chroma_client.get_or_create_collection(name="posts")

    for post in read_posts(DIR):
        chunks = chunk_post(post)
        collection.add(
            ids=[str(uuid.uuid4()) for _ in range(len(chunks))],
            embeddings=[get_embedding(chunk) for chunk in chunks],
            metadatas=[{"year": post.year, "path": str(post.path)} for _ in chunks],
        )


if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "populate":
        populate_vector_db()
        sys.exit(0)

    print(get(arg))
