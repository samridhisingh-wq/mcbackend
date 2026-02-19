from datetime import timedelta

def detect_smurfing(df):
    df = df.sort_values("timestamp")
    results = []
    grouped = df.groupby("receiver_id")

    for receiver, group in grouped:
        if len(group) < 10:
            continue
        window = group.head(10)
        if window["timestamp"].max() - window["timestamp"].min() <= timedelta(hours=72):
            results.append({"receiver": receiver})
    return results
