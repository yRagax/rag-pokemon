from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
OLLAMA_URL = os.getenv("OLLAMA_URL")
TOP_K = int(os.getenv("TOP_K"))
TEMPERATURE = float(os.getenv("TEMPERATURE"))
POKEAPI_BASE=os.getenv("POKEAPI_BASE")
POKEMON_COUNT=int(os.getenv("POKEMON_COUNT"))
