import os, sqlite3, fitz, json

dbpath=r"C:\Users\91735\Downloads\proj\instintive-studio\db\c.sqlite"
safetydocs = r"C:\Users\91735\Downloads\proj\instintive-studio\data\industrial-safety-pdfs"
source = r"C:\Users\91735\Downloads\proj\instintive-studio\data\src.json"
chunk, OVERLAP = 512, 40

def create_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY,
                    doc_title TEXT,
                    doc_file TEXT,
                    doc_url TEXT,
                    chunk_id INTEGER,
                    text TEXT
                )""")
    conn.commit()
    return conn

def chunk_text(text, size=chunk, overlap=OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    return chunks

def load_sources():
    with open(source) as f:
        src = json.load(f)
    mapping = {}
    for item in src:
        key = item["title"].split("—")[0].strip().lower()
        mapping[key] = (item["title"], item["url"])
    return mapping

def match_source(doc_file, sources):
    name = os.path.splitext(doc_file)[0].lower()
    for key, (title, url) in sources.items():
        if key in name:
            return title, url
    return name, None

def ingest_pdfs():
    conn, c = create_db(), None
    c = conn.cursor()
    sources = load_sources()
    for pdf_file in os.listdir(safetydocs):
        if not pdf_file.endswith(".pdf"):
            continue
        doc = fitz.open(os.path.join(safetydocs, pdf_file))
        text = " ".join([p.get_text("text") for p in doc])
        doc_title, doc_url = match_source(pdf_file, sources)
        for idx, chunk in enumerate(chunk_text(text)):
            c.execute("""INSERT INTO chunks (doc_title, doc_file, doc_url, chunk_id, text) VALUES (?,?,?,?,?)""",
                      (doc_title, pdf_file, doc_url, idx, chunk))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ingest_pdfs()
    print("✅ Ingestion complete with titles + URLs in SQLite.")

