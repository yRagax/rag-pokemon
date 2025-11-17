from langchain_ollama import OllamaLLM
from langgraph.errors import GraphRecursionError
from .db import query_pokemon_advanced
from .filter_agent import filter_agent
from .config import TEMPERATURE, USE_HISTORY
from .models import PokemonFilter

llm = OllamaLLM(model="llama3.1:8b", temperature=TEMPERATURE)

async def rag_answer(question: str, history: list[dict] = []):

    try:
        filter = filter_agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })['structured_response']
    except GraphRecursionError:
        filter = PokemonFilter()

    print(f"Filtr:\n{filter}")

    results = query_pokemon_advanced(filter)[:5]
    docs = [r['documents'] for r in results]
    metas = [r['metadatas'] for r in results]
    context = "\n".join(docs)

    print(f"Scalony kontekst:\n{context}")

    final_prompt = (
        "Jesteś pomocnym asystentem Pokémon. "
        "Odpowiedz na pytanie użytkownika dotyczące Pokémonów. "
        "Używaj wyłącznie dostarczonego kontekstu, aby odpowiedzieć. "
        "Musisz podawać źródła wewnątrz tekstu, używając identyfikatorów Pokémonów podanych w kontekście. "
        "Kiedy podajesz informacje o Pokémonie, dodaj odniesienie, np. (ID: 123). "
        "Nie wymyślaj ID Pokémonów. "
        "Używaj wyłącznie identyfikatorów, które pojawiają się w sekcji kontekstowej. "
        "Jeśli nie jesteś pewien, to nie wymyślaj, tylko powiedz 'Nie wiem'.\n\n"
    )

    if USE_HISTORY:
        history_text = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in history)
        print(f"Historia czatu:\n{history_text}")
        final_prompt += f"Historia czatu:\n{history_text}\n\n"

    final_prompt += (
        f"Kontekst:\n{context}\n\n"
        f"Pytanie użytkownika: {question}"
    )

    final_response = llm.invoke(final_prompt)

    print(f"Odpowiedź końcowa:\n{final_response}")

    return {
        "answer": final_response,
        "citations": [{"id": m["id"], "name": m["name"]} for m in metas]
    }
