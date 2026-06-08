import logging
import uuid


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | trace_id=%(trace_id)s | %(message)s",
)


def new_trace_id() -> str:
    return str(uuid.uuid4())


def log_event(message: str, trace_id: str | None = None) -> None:
    if trace_id is None:
        trace_id = new_trace_id()

    logging.info(message, extra={"trace_id": trace_id})
