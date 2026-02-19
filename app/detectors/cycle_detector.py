import networkx as nx

def detect_cycles(G):
    return [c for c in nx.simple_cycles(G) if 3 <= len(c) <= 5]
