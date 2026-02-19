def apply_precision_logic(account, score, G):
    if G.degree(account) > 20:
        score -= 20
    return max(0, min(score, 100))
