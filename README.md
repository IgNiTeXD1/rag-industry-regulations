


## 📖 Project Overview

This project is a **mini Retrieval-Augmented Generation (RAG) system** for industrial and machine safety documents.
It demonstrates:

* Chunking & embedding of \~20 OSHA safety PDFs
* **FAISS similarity search** (semantic retrieval)
* **SQLite BM25 keyword search** (lexical retrieval)
* **Hybrid reranker** that blends both scores
* A **FastAPI API** with a single `/ask` endpoint

---

## ⚙️ Tech Stack

* **Python 3.11+**
* [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) for embeddings
* **FAISS** for vector similarity search
* **SQLite (FTS5)** for BM25 keyword scoring
* **FastAPI** for serving queries

---


## ARCHIETECTURE
PDFs → ingest.py → chunks.sqlite → embed_index.py → FAISS + ids.npy
                               ↓
                      SQLite FTS5 (BM25)
                               ↓
                     SearchEngine (vector/keyword)
                               ↓
                   rerank.py (hybrid blending α=0.6)
                               ↓
                         api.py (/ask)
                               ↓
          POST /ask { q, top, mode } → answer + contexts



## 🚀 Setup

1. Clone repo and install dependencies:
 
 ```bash
  git clone 
https://github.com/IgNiTeXD1/rag-industry-regulations
  cd mini-rag-reranker
  pip install -r requirements.txt
   ```

2. Ingest PDFs → SQLite:

   ```bash
   python ingest.py
   ```

3. Build embeddings + FAISS index:

   ```bash
   python embed_index.py
   ```

4. Start API:

   ```bash
   uvicorn api:app --reload --port 8090
   ```

---

## 📡 API Usage

### Request

```bash
curl -X POST "http://127.0.0.1:8090/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "what is OSHA 3170 about",
    "top": 3,
    "mode": "hybrid"
  }'
```

### Response

```json
{
  "answer": "OSHA 3170 is a publication titled 'Safeguarding Equipment and Protecting Employees from Amputations'. It provides guidance on identifying amputation hazards and safeguarding machinery.",
  "contexts": [...],
  "mode": "hybrid"
}
```

---

## 📊 Results

We tested with **8 evaluation questions** (mix of easy/tricky).

* **Baseline (vector only):** Often returned relevant but unfocused chunks.
* **Hybrid reranker:** Consistently boosted precision, especially for technical standards (e.g. *ISO 13849-1*).

---

## ✨ What I Learned

* **Hybrid search (semantic + lexical)** is simple but powerful — much stronger than embeddings alone.
* Small design details matter: clean chunking, linking `src.json` for citations, and careful answer extraction.
* Even a lightweight system (SQLite + FAISS) can handle professional document QA reliably.

---

