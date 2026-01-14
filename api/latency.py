from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# CORS enable (ANY origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

@app.post("/api/latency")
def latency_metrics(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    with open(DATA_FILE) as f:
        data = json.load(f)

    result = {}

    for r in regions:
        records = [x for x in data if x["region"] == r]

        latencies = [x["latency_ms"] for x in records]
        uptimes = [x["uptime"] for x in records]

        result[r] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result
