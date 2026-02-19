def build_explanations(accounts):
    explanations = {}
    for acc in accounts:
        explanations[acc["account_id"]] = f"Account flagged due to patterns: {', '.join(acc['detected_patterns'])}."
    return explanations
