def format_output(accounts, rings, processing_time, explanations):
    return {
        "suspicious_accounts": sorted(accounts, key=lambda x: x["suspicion_score"], reverse=True),
        "fraud_rings": rings,
        "explanations": explanations,
        "summary": {
            "total_accounts_analyzed": len(accounts),
            "suspicious_accounts_flagged": len(accounts),
            "fraud_rings_detected": len(rings),
            "processing_time_seconds": round(processing_time, 2)
        }
    }
