# 🔍 Invenio

> *Invenio* — Latin for *to find, learn, and discover*

An AI-native knowledge workspace that transforms your documents into an intelligent, searchable knowledge base.

## Features
- 📂 Document ingestion (PDF, DOCX, TXT, CSV, XLSX, Images)
- 🔍 Semantic + Hybrid Search
- 💬 RAG-powered AI chat
- 🤖 Multi-Agent reasoning (LangGraph)
- 📚 NLP Analysis (NER, summarization, topics)
- 📊 Analytics Dashboard

## Tech Stack
- **Backend**: FastAPI + PostgreSQL (Neon) + Qdrant + Redis (Upstash)
- **AI**: LangGraph + LangChain + Qwen3 (Ollama) + BAAI embeddings
- **Frontend**: HTML + CSS + JavaScript
- **Deploy**: Render (backend) + Vercel (frontend)

## Development Phases
See [ROADMAP.md](./ROADMAP.md) for full phase breakdown.
---

# 🚀 Installation

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install spaCy Model

```bash
python -m spacy download en_core_web_sm
```

If the above command fails, install the model manually:

```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

Verify the installation:

```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Loaded Successfully!')"
```

---

## Download NLTK Resources

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

# 🤖 Install Ollama

Download Ollama from the official website:

https://ollama.com/download

Start the Ollama server:

```bash
ollama serve
```

Download the language model:

```bash
ollama pull qwen3
```

Download the embedding model:

```bash
ollama pull bge-m3
```

---

# ⚙️ Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Update the following variables inside the `.env` file:

```env
DATABASE_URL=

QDRANT_URL=
QDRANT_API_KEY=

UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

OLLAMA_BASE_URL=http://localhost:11434

LLM_MODEL=qwen3:8b
EMBEDDING_MODEL=bge-m3
```

---

# ▶️ Running the Project

Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger API Documentation:

```text
http://localhost:8000/docs
```

ReDoc Documentation:

```text
http://localhost:8000/redoc
```
