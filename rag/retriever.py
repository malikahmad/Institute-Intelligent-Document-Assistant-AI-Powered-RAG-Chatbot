from flask import current_app
from sqlalchemy import select
from rank_bm25 import BM25Okapi
from extensions import db
from models import Chunk, Document, DocumentGrant
from rag.indexing import embedding_model

def retrieve(question, user):
    stmt = select(Chunk).join(Document)
    if user.role != "admin":
        permitted = select(DocumentGrant.document_id).where(DocumentGrant.user_id == user.id)
        stmt = stmt.where((Document.visibility == "public") | (Document.id.in_(permitted)))
    chunks = db.session.scalars(stmt).all()
    if not chunks: return []
    texts = [c.content for c in chunks]
    model = embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    qvec = model.encode([question], normalize_embeddings=True, convert_to_numpy=True)[0]
    semantic = vectors @ qvec
    bm25 = BM25Okapi([t.lower().split() for t in texts])
    lexical = bm25.get_scores(question.lower().split())
    k = current_app.config["TOP_K"]
    ranks = {}
    for ranking in (sorted(range(len(chunks)), key=lambda i: semantic[i], reverse=True),
                    sorted(range(len(chunks)), key=lambda i: lexical[i], reverse=True)):
        for rank, idx in enumerate(ranking[:k * 3], 1):
            ranks[idx] = ranks.get(idx, 0) + 1 / (60 + rank)
    chosen = sorted(ranks, key=ranks.get, reverse=True)[:k]
    results = [{"chunk": chunks[i], "score": ranks[i]} for i in chosen]
    if current_app.config["ENABLE_RERANKER"] and results:
        try:
            from sentence_transformers import CrossEncoder
            reranker = CrossEncoder(current_app.config["RERANKER_MODEL"])
            scores = reranker.predict([(question, x["chunk"].content) for x in results])
            for item, score in zip(results, scores): item["rerank_score"] = float(score)
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
        except Exception: current_app.logger.exception("Cross encoder reranking failed")
    return results
