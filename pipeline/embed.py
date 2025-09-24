import sqlite3, numpy as np, faiss, os
from sentence_transformers import SentenceTransformer

dbpath,indexpath,nppath = r"C:\Users\91735\Downloads\proj\instintive-studio\db\c.sqlite", r"C:\Users\91735\Downloads\proj\instintive-studio\db\faiss.index", r"C:\Users\91735\Downloads\proj\instintive-studio\db\ids.npy"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
def build_faiss():
    conn = sqlite3.connect(dbpath)
    rows = conn.execute("SELECT id, text FROM chunks").fetchall()
    conn.close()

    model = SentenceTransformer(MODEL)
    texts, ids = [r[1] for r in rows], [r[0] for r in rows]
    embeddings = model.encode(texts, batch_size=32, convert_to_numpy=True, show_progress_bar=True)

    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs("db", exist_ok=True)
    faiss.write_index(index, indexpath)
    np.save(nppath, np.array(ids))
    print(f"✅ FAISS index built with {len(ids)} chunks.")

if __name__ == "__main__":
    build_faiss()

