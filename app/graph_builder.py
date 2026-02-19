import networkx as nx

def build_graph(df):
    G = nx.DiGraph()
    df = df.sort_values(by="timestamp")

    for _, row in df.iterrows():
        G.add_edge(str(row["sender_id"]), str(row["receiver_id"]),
                   amount=float(row["amount"]),
                   timestamp=row["timestamp"])
    return G
