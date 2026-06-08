from typing import Optional


class ExactCache:
    """
    Cache exato em memória para reduzir chamadas repetidas ao LLM.
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self.hits = 0
        self.misses = 0

    def normalize(self, question: str) -> str:
        return " ".join(question.lower().strip().split())

    def get(self, question: str) -> Optional[str]:
        key = self.normalize(question)

        if key in self._store:
            self.hits += 1
            return self._store[key]

        self.misses += 1
        return None

    def set(self, question: str, answer: str) -> None:
        key = self.normalize(question)
        self._store[key] = answer

    def stats(self) -> dict:
        total = self.hits + self.misses
        hit_rate = self.hits / total if total else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
