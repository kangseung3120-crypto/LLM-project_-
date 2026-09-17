from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

sentences = [
    "고양이가 소파 위에 있다",
    "소파 위에 고양이가 앉아 있다",
    "오늘 주식시장이 상승했다",
]

embeddings = model.encode(sentences)

print("문장 개수:", len(sentences))
print("임베딩 벡터 shape:", embeddings.shape)

similarity = cosine_similarity(embeddings)

print("\nCosine Similarity:")
print(similarity)