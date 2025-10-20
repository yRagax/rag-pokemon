from sentence_transformers import SentenceTransformer
import chromadb
import ollama
from .config import EMBEDDING_MODEL, CHROMA_PATH, TEMPERATURE, TOP_K

embedder = SentenceTransformer(EMBEDDING_MODEL)
collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection("pokemon")
ollama_client = ollama.Client()

async def rag_answer(question: str):
    """
    Multi-step RAG:
    1. LLM rozbija pytanie na 3 podzapytania.
    2. Każde podzapytanie wyszukuje dokumenty w Chroma.
    3. Ostateczna odpowiedź powstaje na podstawie 3 kontekstów.
    """

    sub_prompt = (
        "Rozbij poniższe pytanie użytkownika na 3 prostsze, krótkie, logiczne podzapytania, "
        "które pytają o inny fragment oryginalnego pytania, oraz razem pomogą odpowiedzieć na to pytanie. "
        "Zwróć je jako listę numerowaną bez dodatkowych komentarzy.\n\n"
        f"Pytanie: {question}"
    )

    sub_res = ollama_client.generate(model="llama3.1", prompt=sub_prompt, options={"temperature": 0})
    sub_text = sub_res["response"].strip()

    subqueries = [line.split(".", 1)[-1].strip() for line in sub_text.splitlines() if line.strip()]
    subqueries = [q for q in subqueries if len(q) > 3][:3]
    print("Podzapytania:", subqueries)

    if not subqueries:
        subqueries = [question]

    all_contexts = []

    metas_all = []
    for sq in subqueries:
        q_emb = embedder.encode(sq).tolist()
        results = collection.query(query_embeddings=[q_emb], n_results=TOP_K)

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        metas_all.extend(metas)

        # context = "\n\n".join([f"[{m['id']}] {m['name']}: {d}" for d, m in zip(docs, metas)])
        context = "\n\n".join(docs)
        # all_contexts.append(f"### Podzapytanie: {sq}\n{context}")
        all_contexts.append(context)

    merged_context = "\n\n".join(all_contexts)
    print(f"Scalony kontekst:\n{merged_context}")

    final_prompt = (
        "Jesteś pomocnym asystentem Pokémon. "
        "Używaj wyłącznie dostarczonego kontekstu, aby odpowiedzieć. "
        "Jeśli nie jesteś pewien, to nie wymyślaj, tylko powiedz, że nie wiesz.\n"
        "Kontekst:\n"
        "{context}\n"
        "Pytanie użytkownika: {question}"
    ).format(context=merged_context, question=question)

    final_res = ollama_client.generate(
        model="llama3.1",
        prompt=final_prompt,
        options={"temperature": TEMPERATURE},
    )

    return {
        "answer": final_res["response"],
        "subqueries": subqueries,
        "citations": [{"id": m["id"], "name": m["name"]} for m in metas_all]
    }
