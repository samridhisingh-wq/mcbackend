def score_account(patterns):
    score = 0
    if "cycle" in patterns: score += 50
    if "smurfing" in patterns: score += 30
    if "shell" in patterns: score += 35
    return min(score, 100)
