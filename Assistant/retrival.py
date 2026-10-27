
from langchain_ollama import ChatOllama,OllamaEmbeddings
from pydantic import BaseModel, Field

from Assistant import config, repository
from Assistant.models import Hit, User



class _Rating(BaseModel):
    index: int = Field(description="Number of the chunk being rated")
    score: int = Field(description="0 means useless, 10 means it fully answers the question")


#structure of multiple ratings as llms needs to return multiple ratings
class _Ratings(BaseModel):
    ratings: list[_Rating] = Field(description="One rating per candidate")


# complete retrieval process

class Retriever:
    """Hybrid search with reranking, inside one caller's permissions."""

#conver users question into embedding vector
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
        self.reranker = ChatOllama(
            model=config.HELPER_MODEL, temperature=0
        ).with_structured_output(_Ratings)

#
    def search(
        self, connection, question: str, user: User, include_history: bool = False
    ) -> list[Hit]:
        """The connection is passed in, so it can come from the pool per request."""
        query_vector = self.embeddings.embed_query(question)

        candidates = repository.hybrid_search(
            connection, question, query_vector, user, include_history
        )
        if not candidates:
            return []

        return self._rerank(question, candidates)

    def _rerank(self, question: str, candidates: list[Hit]) -> list[Hit]:
        numbered = "\n".join(
            f"[{number}] {' '.join(hit.content.split())}"
            for number, hit in enumerate(candidates, start=1)
        )

        result = self.reranker.invoke(
            config.prompt("rerank").format(question=question, candidates=numbered)
        )

        scored = []
        for rating in result.ratings:
            if 1 <= rating.index <= len(candidates):
                hit = candidates[rating.index - 1]
                hit.score = rating.score
                scored.append(hit)

        scored.sort(key=lambda hit: hit.score, reverse=True)
        return [hit for hit in scored[: config.TOP_K] if hit.score >= config.MIN_RERANK_SCORE]