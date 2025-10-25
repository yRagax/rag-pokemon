import chromadb
from .config import CHROMA_PATH
from .models import PokemonFilter

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("pokemon")

def query_pokemon_advanced(query: PokemonFilter):

    results = collection.get()
    docs = [{'documents': d, 'metadatas': m, 'ids': i} for d, m, i in zip(results['documents'], results['metadatas'], results['ids'])]

    if query.field and query.value:
        docs = [d for d in docs if all(v.lower() in d['metadatas'].get(query.field, []).lower() for v in query.value)]

    if query.sort_by:
        docs = sorted(
            docs,
            key=lambda x: x['metadatas'].get(query.sort_by),
            reverse=(query.sort_order == "desc")
        )

    if query.limit:
        docs = docs[:query.limit]

    return docs
