from sentence_transformers import SentenceTransformer
import chromadb
import ollama
from .config import EMBEDDING_MODEL, CHROMA_PATH, TEMPERATURE, TOP_K

embedder = SentenceTransformer(EMBEDDING_MODEL)
collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection("pokemon")
ollama_client = ollama.Client()

async def rag_answer(question: str):
    q_emb = embedder.encode(question).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=TOP_K)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    context = "\n\n".join([f"[{m['id']}] {m['name']}: {d}" for d, m in zip(docs, metas)])

    prompt = (
        "Jesteś pomocnym asystentem Pokémon. "
        "Używaj wyłącznie dostarczonego kontekstu, aby odpowiedzieć. "
        "Jeśli nie jesteś pewien, to nie wymyślaj, tylko powiedz, że nie wiesz.\n"
        "Kontekst:\n"
        "{context}\n"
        "Pytanie użytkownika: {question}"
    ).format(context=context, question=question)

    answer = ollama_client.generate(model="llama3.1", prompt=prompt, options={"temperature": TEMPERATURE})
    return {"answer": answer, "citations": [{"id": m["id"], "name": m["name"]} for m in metas]}
