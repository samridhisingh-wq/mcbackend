class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[ry] = rx

def merge_rings(patterns):
    uf = UnionFind()
    for pattern in patterns:
        for i in range(len(pattern)-1):
            uf.union(pattern[i], pattern[i+1])

    rings = {}
    for pattern in patterns:
        for node in pattern:
            root = uf.find(node)
            rings.setdefault(root, set()).add(node)

    return [{"ring_id": f"RING_{i+1:03}",
             "member_accounts": sorted(list(m)),
             "pattern_type": "structural",
             "risk_score": 80.0}
            for i, m in enumerate(rings.values())]
