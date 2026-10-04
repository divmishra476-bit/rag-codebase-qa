# src/observability/tracer.py
import time
import logging
import json
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("rag_pipeline")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class TraceEvent:
    query: str
    stages: dict = field(default_factory=dict)
    total_latency_ms: float = 0.0
    retrieved_chunk_ids: list = field(default_factory=list)
    answer_length: int = 0


class Tracer:
    def __init__(self, query: str):
        self.event = TraceEvent(query=query)
        self._start_time = time.perf_counter()
        self._stage_start = None
        self._current_stage = None

    def start_stage(self, name: str):
        self._current_stage = name
        self._stage_start = time.perf_counter()

    def end_stage(self):
        if self._current_stage is None:
            return
        elapsed_ms = (time.perf_counter() - self._stage_start) * 1000
        self.event.stages[self._current_stage] = round(elapsed_ms, 2)
        self._current_stage = None

    def finish(self, retrieved_chunk_ids: list, answer: str):
        self.event.total_latency_ms = round((time.perf_counter() - self._start_time) * 1000, 2)
        self.event.retrieved_chunk_ids = retrieved_chunk_ids
        self.event.answer_length = len(answer)
        logger.info(json.dumps(asdict(self.event)))