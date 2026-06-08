import statistics
import time

from src.pipeline.rag import answer, cache_stats


QUESTIONS = [
    "O que diz o artigo 7 da LGPD?",
    "Qual a diferença entre controlador e operador?",
    "Posso armazenar CPF de clientes para emissão de nota fiscal?",
    "O que a LGPD diz sobre consentimento?",
    "Quais cuidados devo ter ao armazenar dados pessoais?",

    # Repetidas para testar cache
    "O que diz o artigo 7 da LGPD?",
    "Qual a diferença entre controlador e operador?",
    "Posso armazenar CPF de clientes para emissão de nota fiscal?",
    "O que a LGPD diz sobre consentimento?",
    "Quais cuidados devo ter ao armazenar dados pessoais?",
]


def percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = int(round(0.95 * (len(sorted_values) - 1)))
    return sorted_values[index]


def main() -> None:
    latencies = []

    print("Iniciando benchmark do LGPD Helper...\n")

    for index, question in enumerate(QUESTIONS, start=1):
        start = time.time()
        result = answer(question)
        end = time.time()

        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)

        print(f"[{index}] {question}")
        print(f"    Cache hit: {result.get('cache_hit')}")
        print(f"    Complexidade: {result.get('complexity')}")
        print(f"    Latência: {latency_ms:.2f} ms")
        print()

    stats = cache_stats()

    total_queries = len(QUESTIONS)
    cache_hits = stats["hits"]
    cache_misses = stats["misses"]

    baseline_llm_calls = total_queries
    optimized_llm_calls = cache_misses

    reduction = (
        (baseline_llm_calls - optimized_llm_calls) / baseline_llm_calls
        if baseline_llm_calls
        else 0
    )

    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print(f"Total de perguntas: {total_queries}")
    print(f"Cache hits: {cache_hits}")
    print(f"Cache misses: {cache_misses}")
    print(f"Hit-rate: {stats['hit_rate']:.2%}")
    print(f"Chamadas LLM baseline: {baseline_llm_calls}")
    print(f"Chamadas LLM otimizadas: {optimized_llm_calls}")
    print(f"Redução estimada de chamadas LLM: {reduction:.2%}")
    print(f"Latência média: {statistics.mean(latencies):.2f} ms")
    print(f"P95 latency: {percentile_95(latencies):.2f} ms")


if __name__ == "__main__":
    main()
