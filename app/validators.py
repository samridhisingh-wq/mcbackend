import pandas as pd

REQUIRED_COLUMNS = [
    "transaction_id",
    "sender_id",
    "receiver_id",
    "amount",
    "timestamp",
]

def validate_csv(df: pd.DataFrame) -> pd.DataFrame:
    # 1️⃣ Check required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # 2️⃣ Convert timestamp
    try:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="%Y-%m-%d %H:%M:%S"
        )
    except Exception:
        raise ValueError("Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")

    # 3️⃣ Convert amount
    try:
        df["amount"] = df["amount"].astype(float)
        if not (df["amount"] > 0).all():
            raise ValueError("Amount must be positive")
    except Exception:
        raise ValueError("Invalid amount column")

    # 🔥 RETURN CLEANED DATAFRAME
    return df
