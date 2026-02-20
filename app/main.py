from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import time
import uuid

# Your existing modules
from app.validators import validate_csv
from app.graph_builder import build_graph
from app.detectors.cycle_detector import detect_cycles
from app.detectors.smurfing_detector import detect_smurfing
from app.detectors.shell_detector import detect_shell_chains
from app.detectors.ring_merger import merge_rings
from app.scoring import score_account
from app.formatter import format_output
from app.precision import apply_precision_logic
from app.explanation import build_explanations


app = FastAPI(
    title="MuleCatcher AML Engine",
    description="Explainable, deterministic AML decision-support system",
    version="2.0.0"
)

# 🔥 CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        df = pd.read_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    # Validate
    validate_csv(df)

    # Build graph
    graph = build_graph(df)

    # Run detections
    cycles = detect_cycles(graph)
    smurfing = detect_smurfing(graph)
    shells = detect_shell_chains(graph)

    rings = merge_rings(cycles + smurfing + shells)

    # Score accounts
    accounts = score_account(graph)

    # Apply precision logic
    accounts = apply_precision_logic(accounts)

    # Add explanations
    accounts = build_explanations(accounts)

    # Format final output
    accounts = format_output(accounts)

    # Build edges list for frontend
    edges = []
    for u, v, data in graph.edges(data=True):
        edges.append({
            "from": str(u),
            "to": str(v),
            "amount": data.get("amount", 0),
            "count": data.get("count", 1)
        })

    # Build suspicious accounts list (for compatibility)
    suspicious_accounts = [
        {
            "account_id": acc["id"],
            "suspicion_score": acc["riskScore"],
            "detected_patterns": acc.get("patterns", [])
        }
        for acc in accounts
        if acc["riskScore"] >= 40
    ]

    elapsed = round(time.time() - start_time, 2)

    # Build CaseRun object (matches frontend)
    case = {
        "id": f"CASE-{uuid.uuid4().hex[:8]}",
        "date": time.strftime("%Y-%m-%d"),
        "fileName": file.filename,
        "datasetSize": len(df),
        "nodeCount": len(accounts),
        "edgeCount": len(edges),
        "txCount": len(df),
        "suspiciousCount": len(suspicious_accounts),
        "ringCount": len(rings),
        "processingTime": elapsed,
        "riskExposure": max([acc["riskScore"] for acc in accounts] or [0]),
        "timeWindow": "",
        "topPatterns": list(
            set(
                pattern
                for acc in suspicious_accounts
                for pattern in acc.get("detected_patterns", [])
            )
        ),
        "riskLevel": (
            "high"
            if len(suspicious_accounts) > 5
            else "medium"
            if len(suspicious_accounts) > 2
            else "low"
        ),
    }

    return {
        "cases": [case],
        "currentCase": case,
        "accounts": accounts,
        "rings": rings,
        "edges": edges,
        "suspicious_accounts": suspicious_accounts
    }
