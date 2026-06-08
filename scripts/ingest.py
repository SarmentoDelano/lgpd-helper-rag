import time

from src.pipeline.rag import ingest_and_index


if __name__ == "__main__":
    print("Iniciando indexação do corpus...", flush=True)

    start = time.time()

    try:
        result = ingest_and_index(force_rebuild=True)

        print("\nResultado da indexação:", flush=True)
        print(result, flush=True)

    except Exception as error:
        print("\nERRO DURANTE A INDEXAÇÃO:", flush=True)
        print(type(error).__name__, flush=True)
        print(error, flush=True)
        raise

    end = time.time()
    print(f"\nTempo total: {end - start:.2f} segundos", flush=True)
