# Zadanie rekrutacyjne: Chat z RAG o 200 pierwszych Pokémonach

Masz zbudować mini-system: **RAG-chat** oparty o dane z [PokeAPI](https://pokeapi.co/). System ma odpowiadać na pytania o **pierwsze 200 Pokémonów** (ID 1–200), korzystając z wektorowego wyszukiwania i małego LLM (max ~8B parametrów).

---

## Wymagania funkcjonalne

1. **Ingest danych (ETL)**

   * Funkcja/komenda, która:

     * Pobiera z PokeAPI dane dla Pokémonów 1–200 (co najmniej: `name`, `id`, `types`, `abilities`, `stats`, **gatunek/species** + **flavor_text** z wersji EN, przykładowe `moves` – skrócona lista lub top N; dopuszczalne własne sensowne pole).
     * Normalizuje i **wektoryzuje** treść (np. łączy kluczowe pola do jednego dokumentu tekstowego + metadane).
     * Zapisuje dokumenty + wektory do **bazy wektorowej**.
   * Uruchamiane jedną komendą (np. `pnpm ingest` / `python -m app.ingest` / `make ingest`).

2. **Serwer API (backend)**

   * Endpoint **`POST /chat`**:

     * Wejście: `{ sessionId?, message: string }`.
     * Działanie:

       1. Embed zapytania → wektorowe wyszukiwanie (top-k, np. 3–5),
       2. Złożenie kontekstu (citations/źródła),
       3. Odpowiedź z LLM (≤ 8B), **z ugruntowaniem w źródłach**.
     * Wyjście: `{ answer: string, citations: [{id, name}], usedDocsSnippet?: string[] }`.
   * Endpoint **`GET /health`** – proste sprawdzenie żywotności.
   * **Stateless** albo lekka pamięć sesji (do wyboru), ale bez wylatujących wyjątków.
   * Logowanie zapytań i czasu odpowiedzi.

3. **Frontend (chat)**

   * Prosty UI (może być React/Vue/Svelte) z:

     * Polem input, lista wiadomości,
     * **Wskazaniem użytych źródeł** (np. nazwa pokémona/ID) pod odpowiedzią,
     * Obsługą “enter to send”, stanem “loading”.
   * Minimalny styl – ma być używalne.

4. **Model i wektory**

   * **LLM do 8B** (np. Llama 3.1 8B Instruct, Qwen2 7B, Mistral 7B) – lokalnie (Ollama/LM Studio) lub przez prosty runtime.
   * **Embedding**: open-source (np. `bge-small/e5-small` lub podobny) – konsekwentny między ingest a zapytaniami.
   * **Baza wektorowa**: dowolna (np. Qdrant, PostgreSQL+pgvector, Chroma, Milvus). Musi być uruchamialna lokalnie (preferowany Docker).

---

## Wymagania niefunkcjonalne

* **Deterministyczność**: Ustaw temperaturę modelu ≤ 0.7; w README opisz, jak powtórzyć wynik.
* **Walidacja**: sensowne błędy HTTP (400/500), timeouts, retry na PokeAPI (limit rate).
* **Brak hardcodów kluczy**: jeżeli jakieś są potrzebne – `.env.example`.

---

## Co ma być w repozytorium

1. **Kod**: `backend/`, `frontend/`, `scripts/` (lub inna rozsądna struktura).
2. **Funkcje/komendy ingestu** dla 200 pierwszych Pokémonów.
3. **Serwer z chatem** (endpointy jw.).
4. **Frontend z chatem** (działający z backendem).
5. **README.md** z:

   * Wymaganiami (Ollama/Node/Python…),
   * Instrukcjami uruchomienia (ingest → backend → frontend),
   * Konfiguracją (env),
   * Opisem architektury RAG (diagram mile widziany),
   * Przykładowymi pytaniami testowymi.

---

## Minimalny zakres danych (per Pokémon)

* `id`, `name`, `types[]`, `abilities[]`,
* `stats{hp, attack, defense, sp_atk, sp_def, speed}`,
* `species.name`, `flavor_text` (EN),
* Opcjonalnie: `height`, `weight`, kilka kluczowych `moves[]`.
* **Dokument wektorowy**: zwięzły, ale informacyjny (ok. 300–1000 słów po złączeniu pola/ów); metadane z `id`, `name`, `types`.

---

## Kryteria akceptacji (checklista)

* [ ] Komenda ingestu tworzy/uzupełnia bazę 200 dokumentami + wektorami.
* [ ] `POST /chat` zwraca odpowiedź oraz **co najmniej 1 citation** z listą źródeł (np. `[{id: 25, name: "pikachu"}]`).
* [ ] Frontend wyświetla konwersację i **źródła** pod odpowiedzią.
* [ ] Zapytania typu:

  * “Podaj najszybsze Pokémony z pierwszej dwusetki i ich typy.”
  * “Które elektryczne mają też typ stalowy?”
  * “Porównaj Pikachu i Raichu: staty i zdolności.”
  * “Jaki flavor text ma Bulbasaur w EN?”

  zwracają treść ugruntowaną w dokumentach (nie halucynacje z kosmosu).
* [ ] Projekt uruchamia się na czysto wg README.

---

## Ocena (100 pkt)

1. **RAG pipeline** (30 pkt)

   * Jakość ingestu, normalizacja, embedding, retrieval (top-k, filtracje po metadanych).
2. **Odpowiedzi i ugruntowanie** (25 pkt)

   * Trafność i spójność odpowiedzi, widoczne **citations**, brak oczywistych halucynacji.
3. **Backend/API** (15 pkt)

   * Stabilność, błędy, logi, struktura kodu, proste testy (mile widziane).
4. **Frontend UX** (10 pkt)

   * Czytelność, obsługa stanów, źródła przy odpowiedzi.
5. **DevEx/Uruchamialność** (10 pkt)

   * README, `.env.example`, proste komendy.
6. **Inżynieria** (10 pkt)

   * Architektura, separacja warstw, rozsądne decyzje techniczne.

**Minusy**: hardcode kluczy, brak citations, brak ingestu, “to działa tylko u mnie”.

---

## Dopuszczalne technologie (przykłady)

* **LLM**: Llama 3.1 8B, Qwen2 7B, Mistral 7B (Ollama/LM Studio/gguf).
* **Embeddings**: dowolny np.: nomic.
* **Vector DB**: Qdrant, pgvector (Postgres), Chroma, Milvus.
* **Backend**: Node.js (NestJS/Express/Fastify) lub Python (FastAPI).
* **Frontend**: React/Vite (prosto), Tailwind opcjonalnie.

Wybór jest Twój – byle spójny i dobrze opisany.

---

## Jak oddać

* Link do repo (public/private) z instrukcją uruchomienia
* Prezentacja działania na spotkaniu