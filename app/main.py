from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import time

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

@app.get("/health")
def health_check():
    return {"status": "running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    try:
        df = pd.read_csv(file.file)
    except:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    validation = validate_csv(df)

    if not all([validation["columns_valid"], validation["timestamp_valid"], validation["amount_valid"]]):
        raise HTTPException(status_code=400, detail="CSV validation failed")

    G = build_graph(df)

    cycles = detect_cycles(G)
    smurfing = detect_smurfing(df)
    shell_chains = detect_shell_chains(G)

    rings = merge_rings(cycles + shell_chains)

    account_patterns = {}

    for c in cycles:
        for acc in c:
            account_patterns.setdefault(acc, set()).add("cycle")

    for s in shell_chains:
        for acc in s:
            account_patterns.setdefault(acc, set()).add("shell")

    for s in smurfing:
        account_patterns.setdefault(s["receiver"], set()).add("smurfing")

    suspicious_accounts = []
    for acc, patterns in account_patterns.items():
        score = score_account(patterns)
        score = apply_precision_logic(acc, score, G)
        suspicious_accounts.append({
            "account_id": acc,
            "suspicion_score": score,
            "detected_patterns": list(patterns),
        })

    explanations = build_explanations(suspicious_accounts)

    processing_time = time.time() - start_time

    return format_output(suspicious_accounts, rings, processing_time, explanations)
