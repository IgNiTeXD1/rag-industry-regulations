from sim import SearchEngine

def hybrid_search(q,top=5,alpha=0.6):
    se = SearchEngine()
    ss = se.similaritysearch(q,top*3)
    kw = se.keywordsearch(q,top*3)

    def norm(results):
        scores = [r["score"] for r in results]
        maxs, mins = max(scores) if scores else 1.0, min(scores) if scores else 0.0
        for r in results:
            r["norm"] = 0.5 if maxs == mins else (r["score"] - mins) / (maxs - mins)
        return {r["text"][:50]+r["title"]: r for r in results}

    vec_map, kw_map = norm(ss), norm(kw)

    merged = {}
    for key, r in vec_map.items():
        merged[key] = r.copy()
        merged[key]["final"] = alpha*r["norm"]

    for key, r in kw_map.items():
        if key in merged:
            merged[key]["final"] += (1-alpha)*r["norm"]
        else:
            merged[key] = r.copy()
            merged[key]["final"] = (1-alpha)*r["norm"]

    ranked = sorted(merged.values(), key=lambda x: x["final"], reverse=True)
    return ranked[:top]

if __name__ == "__main__":
    print("Hybrid:", hybrid_search("ISO 13849-1 safety", 2))
