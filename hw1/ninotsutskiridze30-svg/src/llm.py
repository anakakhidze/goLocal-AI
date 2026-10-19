"""Optional provider-neutral model boundary. The offline CLI never invokes it.

Transport is supplied by a future adapter. It returns extraction, tokens_in,
tokens_out. Rates are explicit USD per million tokens, never invented defaults.
"""
import json
import os
from pathlib import Path
from time import perf_counter


def extract_with_model(source_text, *, transport, model, input_rate, output_rate,
                       log_path=Path(__file__).resolve().parent / "logs" / "usage.jsonl"):
    key = os.environ.get("EVENT_MODEL_API_KEY")
    if not key:
        raise RuntimeError("Set EVENT_MODEL_API_KEY in the shell environment.")
    if input_rate < 0 or output_rate < 0:
        raise ValueError("Usage rates must be nonnegative.")
    start = perf_counter()
    response = None
    try:
        response = transport(source_text=source_text, api_key=key, model=model)
        return response["extraction"]
    finally:
        tokens_in = response.get("tokens_in") if response else None
        tokens_out = response.get("tokens_out") if response else None
        usage = {"model": model, "tokens_in": tokens_in, "tokens_out": tokens_out,
                 "cost_usd": ((tokens_in * input_rate + tokens_out * output_rate) / 1_000_000
                              if tokens_in is not None and tokens_out is not None else None),
                 "latency_ms": round((perf_counter() - start) * 1000, 3)}
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(usage) + "\n")
