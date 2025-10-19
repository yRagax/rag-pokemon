import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm
from sentence_transformers import SentenceTransformer
import chromadb
from backend.config import CHROMA_PATH, EMBEDDING_MODEL, POKEAPI_BASE, POKEMON_COUNT


client = httpx.AsyncClient(timeout=15.0)
embedder = SentenceTransformer(EMBEDDING_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("pokemon")


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_json(url: str):
    """Bezpieczne pobieranie JSON z retry/backoff"""
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.json()


def normalize_flavor_text(entries):
    """Zwraca 1 sensowny flavor text po angielsku"""
    for entry in entries:
        if entry["language"]["name"] == "en":
            text = entry["flavor_text"]
            text = text.replace("\n", " ").replace("\f", " ").strip()
            return text
    return ""


def build_document(pokemon_data, species_data):
    """Łączy dane o Pokémonie w jeden opisowy tekst"""
    name = pokemon_data["name"].capitalize()
    pid = pokemon_data["id"]

    types = ", ".join([t["type"]["name"] for t in pokemon_data["types"]])
    abilities = ", ".join([a["ability"]["name"] for a in pokemon_data["abilities"]])
    stats = {s["stat"]["name"]: s["base_stat"] for s in pokemon_data["stats"]}
    moves = [m["move"]["name"] for m in pokemon_data["moves"][:5]]

    height = pokemon_data["height"]
    weight = pokemon_data["weight"]
    flavor_text = normalize_flavor_text(species_data.get("flavor_text_entries", []))

    doc_text = (
        f"{name} (ID: {pid}) to Pokémon typu: {types}. "
        f"Posiada umiejętności: {abilities}. "
        f"Podstawowe statystyki to: HP {stats.get('hp')}, Atak {stats.get('attack')}, "
        f"Obrona {stats.get('defense')}, Sp. Atak {stats.get('special-attack')}, "
        f"Sp. Obrona {stats.get('special-defense')}, Szybkość {stats.get('speed')}. "
        f"Wysokość: {height}, Waga: {weight}. "
        f"Przykładowe ruchy to: {', '.join(moves)}. "
        f"Gatunek Pokémona: {species_data['name']}. "
        f"Opis: {flavor_text}"
    )

    metadata = {
        "id": pid,
        "name": name,
        "types": ", ".join([t["type"]["name"] for t in pokemon_data["types"]]),
        "abilities": ", ".join([a["ability"]["name"] for a in pokemon_data["abilities"]]),
    }

    return doc_text, metadata


async def ingest():
    print("Starting Pokémon data ingestion...")
    docs, metas, ids = [], [], []

    for pid in tqdm(range(1, POKEMON_COUNT + 1), desc="Fetching Pokémon"):
        try:
            pokemon_url = f"{POKEAPI_BASE}/pokemon/{pid}"
            species_url = f"{POKEAPI_BASE}/pokemon-species/{pid}"

            pokemon_data = await fetch_json(pokemon_url)
            species_data = await fetch_json(species_url)

            doc_text, metadata = build_document(pokemon_data, species_data)
            docs.append(doc_text)
            metas.append(metadata)
            ids.append(str(pid))

        except Exception as e:
            print(f"Error fetching Pokémon {pid}: {e}")

    print(f"Fetched {len(docs)} Pokémon entries. Now embedding...")

    embeddings = embedder.encode(docs, show_progress_bar=True, convert_to_numpy=False)
    embeddings = [e.tolist() for e in embeddings]

    print(f"Saving to ChromaDB at {CHROMA_PATH} ...")
    print(f"metadata: {metas[0]}")
    collection.add(documents=docs, embeddings=embeddings, metadatas=metas, ids=ids)

    print("Ingestion complete! (200 Pokémon saved)")
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(ingest())
