from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sim import SearchEngine
from rerank import hybrid_search
import re

app = FastAPI()
se = SearchEngine()


class AskReq(BaseModel):
    q: str
    top: int = 3
    mode: str = "vector"  


def extract_answer(contexts, query, max_len=400):
  
    query_terms = [w.lower() for w in query.split() if len(w) > 2]

    
    for ctx in contexts[:3]:
        sentences = re.split(r'(?<=[.!?])\s+', ctx["text"].strip())
        for s in sentences:
            if any(term in s.lower() for term in query_terms):
                return s if len(s) < max_len else s[:max_len] + "..."
            

    """ if any(word.lower() in s.lower() for word in query.split()):
            return s if len(s) < max_len else s[:max_len] + "..."" """

    # Fallback: first 2 sentences of the top chunk
    if contexts:
        top_sentences = re.split(r'(?<=[.!?])\s+', contexts[0]["text"].strip())
        if top_sentences:
            return " ".join(top_sentences[:2])[:max_len]

    return None


@app.post("/ask")
def ask(req: AskReq):
    # Run retrieval
    if req.mode == "vector":
        results = se.similaritysearch(req.q, req.top)
    elif req.mode == "keyword":
        results = se.keywordsearch(req.q, req.top)
    else:
        results = hybrid_search(req.q, req.top)

    # Smarter answer extraction
    answer = (
        extract_answer(results, req.q)
        if results and results[0]["score"] > 0.3
        else None
    )

    return {"answer": answer, "contexts": results, "mode": req.mode}

