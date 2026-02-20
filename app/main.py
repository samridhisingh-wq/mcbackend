from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    version="2.0.0",
)

# 🔥 CORS (IMPORTANT FOR FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon/demo. Lock later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Health check
@app.get("/health")
def health():
    return {"status": "running"}


# ✅ MAIN ANALYZE ENDPOINT
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        # 1️⃣ Read CSV into DataFrame
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))

        # 2️⃣ Validate
        df = validate_csv(df)

        # 3️⃣ Build Graph
        graph = build_graph(df)

        # 4️⃣ Run detectors correctly
        cycles = detect_cycles(graph)          # graph-based
        smurfing = detect_smurfing(df)         # dataframe-based ✅
        shell_chains = detect_shell_chains(graph)

        # 5️⃣ Merge suspicious structures
        merged_rings = merge_rings(cycles, smurfing, shell_chains)

        # 6️⃣ Score accounts
        scored_accounts = score_account(df, merged_rings)

        # 7️⃣ Apply precision logic
        final_accounts = apply_precision_logic(scored_accounts)

        # 8️⃣ Build explanations
        explanations = build_explanations(final_accounts)

        # 9️⃣ Format final output
        response = format_output(
            accounts=final_accounts,
            rings=merged_rings,
            graph=graph,
            explanations=explanations
        )

        processing_time = round(time.time() - start_time, 2)

        response["processing_time"] = processing_time

        return response

    except Exception as e:
        print("ANALYZE ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
