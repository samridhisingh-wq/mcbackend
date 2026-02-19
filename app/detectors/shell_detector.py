import networkx as nx

def detect_shell_chains(G):
    chains = []
    for node in G.nodes():
        for path in nx.single_source_shortest_path(G, node, cutoff=4).values():
            if len(path) >= 4:
                intermediates = path[1:-1]
                if all(G.degree(n) <= 3 for n in intermediates):
                    chains.append(path)
    return chains
