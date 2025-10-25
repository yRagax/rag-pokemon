from langchain_ollama import OllamaLLM
from .db import query_pokemon_advanced
from .filter_agent import filter_agent
from .config import TEMPERATURE

llm = OllamaLLM(model="llama3.1:8b", temperature=TEMPERATURE)

async def rag_answer(question: str):

    filter = filter_agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    print(f"Filtr:\n{filter["structured_response"]}")

    results = query_pokemon_advanced(filter["structured_response"])[:5]
    docs = [r['documents'] for r in results]
    metas = [r['metadatas'] for r in results]
    context = "\n".join(docs)

    print(f"Scalony kontekst:\n{context}")

    final_prompt = (
        "Jesteś pomocnym asystentem Pokémon. "
        "Odpowiedz na pytanie użytkownika dotyczące się Pokémonów. "
        "Używaj wyłącznie dostarczonego kontekstu, aby odpowiedzieć. "
        "Jeśli nie jesteś pewien, to nie wymyślaj, tylko powiedz, 'Nie wiem'.\n"
        "Kontekst:\n"
        "{context}\n"
        "Pytanie użytkownika: {question}"
    ).format(context=context, question=question)

    final_response = llm.invoke(final_prompt)

    print(f"Odpowiedź końcowa:\n{final_response}")

    return {
        "answer": final_response,
        "citations": [{"id": m["id"], "name": m["name"]} for m in metas]
    }
