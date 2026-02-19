import pandas as pd

REQUIRED_COLUMNS = ["transaction_id","sender_id","receiver_id","amount","timestamp"]

def validate_csv(df):
    summary = {"columns_valid": True,"timestamp_valid": True,"amount_valid": True}

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            summary["columns_valid"] = False

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")
    except:
        summary["timestamp_valid"] = False

    try:
        df["amount"] = df["amount"].astype(float)
        if not (df["amount"] > 0).all():
            summary["amount_valid"] = False
    except:
        summary["amount_valid"] = False

    return summary
