import argparse
import json

from .api import align_hypergraphs
from .io import load_ground_truth, load_hypergraph, load_seed_pairs, save_matches
from .metrics import evaluate_alignment


def main():
    parser = argparse.ArgumentParser(description="ISHA: hypergraph alignment from seed hyperedge correspondences.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--seeds", required=True, help="CSV with zero-based source_edge,target_edge indices.")
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--output", default="outputs/matches.csv")
    parser.add_argument("--ground-truth", help="Optional source,target CSV used only for evaluation.")
    args = parser.parse_args()
    source, target = load_hypergraph(args.source), load_hypergraph(args.target)
    seeds = load_seed_pairs(args.seeds, source, target)
    matches = align_hypergraphs(source, target, seeds, max_rounds=args.max_rounds)
    save_matches(args.output, matches)
    result = {"predicted_matches": len(matches), "output": args.output}
    if args.ground_truth:
        result.update(evaluate_alignment(matches, load_ground_truth(args.ground_truth)))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
