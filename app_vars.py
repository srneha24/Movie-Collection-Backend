import os
from dotenv import load_dotenv


load_dotenv()

ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")

MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY")
MEILISEARCH_HOST = os.getenv("MEILISEARCH_HOST")

INDEX_NAME = os.getenv("INDEX_NAME")

ENGINE_TO_USE = os.getenv("ENGINE_TO_USE")
