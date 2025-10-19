# RAG Pokémon Chat (Python + FastAPI + Chroma + Ollama + Gradio)

Projekt demonstracyjny systemu **Retrieval-Augmented Generation (RAG)** opartego na danych z **PokeAPI**.  
Chatbot odpowiada na pytania o **pierwsze 200 Pokémonów**, korzystając z lokalnej bazy wektorowej (ChromaDB)  
i modelu **Llama 3.1 8B** uruchamianego przez **Ollama**.

---

## Funkcjonalności

- Pobiera dane z [PokeAPI](https://pokeapi.co) dla Pokémonów `1–200`  
- Tworzy lokalną bazę dokumentów i embeddingów w **ChromaDB**  
- Obsługuje przez prosty frontend **Gradio**  
- Generuje odpowiedzi ugruntowane w źródłach (`citations`)  
- Lokalny, bez zewnętrznych kluczy API

---

## Technologie

| Komponent | Technologia |
|------------|--------------|
| **LLM** | Llama 3.1 8B (przez [Ollama](https://ollama.com/)) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector DB** | [ChromaDB](https://www.trychroma.com/) (lokalnie w katalogu `data/chroma`) |
| **Backend** | Python + FastAPI |
| **Frontend** | Python + Gradio |
| **Źródło danych** | [PokeAPI](https://pokeapi.co) |

---

## Wymagania

- Python **3.12+**
- [Ollama](https://ollama.com/download) (z zainstalowanym modelem `llama3:8b`)
- Virtualenv lub Conda

---

## Instalacja

```bash
# 1. Klonuj repo
git clone https://github.com/yRagax/rag-pokemon.git
cd rag-pokemon

# 2. Utwórz i aktywuj środowisko
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# lub
.venv\Scripts\activate      # Windows

# 3. Zainstaluj zależności
pip install -r requirements.txt
```

---

## Konfiguracja środowiska

Skopiuj plik `.env.example` do `.env` i dostosuj jeśli trzeba:

```bash
cp .env.example .env
```

---

## Krok 1 — Ingest danych

Pobiera dane o 200 Pokémonach i zapisuje embeddingi w lokalnej bazie.

```bash
python -m backend.ingest
```
Wynik: katalog data/chroma/ z zapisanymi wektorami i metadanymi Pokémonów.

---

## Krok 2 — Uruchom backend API

```bash
uvicorn backend.api:app --reload --port 8000
```

Domyślnie backend działa pod ```http://localhost:8000```.

### Endpointy:

| Endpoint  | Metoda | Opis                             |
| --------- | ------ | -------------------------------- |
| `/health` | GET    | Proste sprawdzenie statusu       |
| `/chat`   | POST   | Chat RAG: `{ "message": "..." }` |

Przykład:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Podaj najszybsze Pokémony z pierwszej dwusetki"}'
```

---

## Krok 3 — Uruchom frontend (Gradio)

```bash
python -m frontend.ui
```

Po uruchomieniu otworzy się przeglądarka pod adresem: ```http://localhost:7860```.\
Zobaczysz prosty chat z polami:
- ✅ pytanie użytkownika
- ✅ odpowiedź modelu
- ✅ cytowane źródła (np. „Pikachu (#25)”, „Raichu (#26)”)

---

## Architektura RAG

             ┌─────────────────────┐
             │  User / Gradio Chat │
             └──────────┬──────────┘
                        │ message
                        ▼
                 ┌──────────────┐
                 │   FastAPI    │
                 │  (backend)   │
                 └──────┬───────┘
                        │
         ┌──────────────┼─────────────────────┐
         ▼              ▼                     ▼
      ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
      │ Embed Model  │ │  ChromaDB    │ │ Llama 3.1 8B   │
      │ (MiniLM)     │ │(vector store)│ │ (Ollama)       │
      └──────────────┘ └──────────────┘ └────────────────┘
               │              │                     │
               │              └── context (top-k) ──┘
               │
               └──→ Response → citations → frontend

---

## Przykładowe zapytania

Spróbuj w chatcie:

| Pytanie                                                          | Co sprawdza                     |
| ---------------------------------------------------------------- | ------------------------------- |
| **"Podaj najszybsze Pokémony z pierwszej dwusetki i ich typy."** | test retrievalu po statystykach |
| **"Które elektryczne mają też typ stalowy?"**                    | test semantyczny po typach      |
| **"Porównaj Pikachu i Raichu: staty i zdolności."**              | test porównawczy                |
| **"Jaki flavor text ma Bulbasaur w EN?"**                        | test species/flavor_text        |

---

## Struktura projektu

```bash
rag-pokemon/
├── backend/
│   ├── api.py
│   ├── config.py
│   ├── ingest.py
│   └── rag_chain.py
│
├── frontend/
│   └── ui.py
│
├── data/
│   └── chroma/
│
├── .env.example
├── TASK.md
└── README.md
```

---

## Powtarzalność wyników

- Ustawiona temperatura modelu: ≤ 0.7 (domyślnie 0.3)
- Deterministyczne embeddingi (all-MiniLM-L6-v2)
- Wszystkie dane lokalne — wyniki możliwe do odtworzenia 1:1

---

## Wskazówki developerskie

- Jeśli chcesz wyczyścić bazę:
```bash
rm -rf data/chroma
```
- Jeśli zmienisz model embeddingów – wykonaj ingest ponownie.
- Ollama musi działać w tle:
```bash
ollama serve
```

---

## Checklista uruchomienia

- ```python -m backend.ingest``` — utworzono bazę 200 Pokémonów
- ```uvicorn backend.api:app --reload --port 8000``` — backend działa (```/health```)
- ```python -m frontend.ui``` — chat w przeglądarce
- Odpowiedzi zawierają citations
- Wszystko działa offline i deterministycznie

---

## Autor

Projekt rekrutacyjny — Pokémon RAG Chat, Filip Szyszko\
Stack: Python / FastAPI / Gradio / ChromaDB / Ollama / Llama 3.1 8B

---
