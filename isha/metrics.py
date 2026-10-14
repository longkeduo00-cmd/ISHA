def evaluate_alignment(matches, ground_truth):
    """Evaluate predicted node pairs against an explicit ground-truth mapping."""
    matches, ground_truth = dict(matches), dict(ground_truth)
    if len(set(matches.values())) != len(matches):
        raise ValueError("Predicted alignment must be one-to-one.")
    if len(set(ground_truth.values())) != len(ground_truth):
        raise ValueError("Ground truth must be one-to-one.")
    correct = sum(source in ground_truth and target == ground_truth[source] for source, target in matches.items())
    predicted, total = len(matches), len(ground_truth)
    return {
        "precision": correct / predicted if predicted else 0.0,
        "recall": correct / total if total else 0.0,
        "f1": 2 * correct / (predicted + total) if predicted + total else 0.0,
        "correct_matches": correct,
        "predicted_matches": predicted,
        "ground_truth_total": total,
    }
