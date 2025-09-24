
import sqlite3, numpy as np, faiss
from sentence_transformers import SentenceTransformer

dbpath = r"C:\Users\91735\Downloads\proj\instintive-studio\db\c.sqlite"
indexpath = r"C:\Users\91735\Downloads\proj\instintive-studio\db\faiss.index"
nppath = r"C:\Users\91735\Downloads\proj\instintive-studio\db\ids.npy"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class SearchEngine:
    def __init__(self):
        self.conn = sqlite3.connect(dbpath)
        self.model = SentenceTransformer(MODEL)
        self.index = faiss.read_index(indexpath)
        self.ids = np.load(nppath)

    #similarity
    def similaritysearch(self, q, top=10):
        qemb = self.model.encode([q], convert_to_numpy=True)
        faiss.normalize_L2(qemb)
        D, I = self.index.search(qemb, top)
        results = []
        for score, idx in zip(D[0], I[0]):
            chunk_id = int(self.ids[idx])
            row = self.conn.execute(
                "SELECT doc_title, doc_url, text FROM chunks WHERE id=?",
                (chunk_id,)
            ).fetchone()
            results.append({
                "text": row[2],
                "title": row[0],
                "url": row[1],
                "score": float(score)
            })
        return results

    # keyword
    def keywordsearch(self, q, top=5):
        def escape_query(q: str) -> str:
           
            if "-" in q or any(ch.isdigit() for ch in q):
                return f'"{q}"'
            return q

        q = escape_query(q)

        c = self.conn.cursor()
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(id, text)")
        if c.execute("SELECT COUNT(*) FROM fts_chunks").fetchone()[0] == 0:
            rows = self.conn.execute("SELECT id, text FROM chunks").fetchall()
            c.executemany("INSERT INTO fts_chunks (id, text) VALUES (?, ?)", rows)
            self.conn.commit()

        rows = c.execute(
            """
            SELECT id, bm25(fts_chunks) AS rank
            FROM fts_chunks
            WHERE fts_chunks MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (q, top*2)
        ).fetchall()

        results = []
        for cid, score in rows:
            row = self.conn.execute(
                "SELECT doc_title, doc_url, text FROM chunks WHERE id=?",
                (cid,)
            ).fetchone()
            results.append({
                "text": row[2],
                "title": row[0],
                "url": row[1],
                "score": int(0-score)  
            })
        return results[:top]


if __name__ == "__main__":
    se = SearchEngine()
    print("Vector:", se.similaritysearch("ISO 13849-1 safety", 2))
    print("Keyword:", se.keywordsearch("ISO 13849-1", 2))
