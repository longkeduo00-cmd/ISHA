from operator import index

from .core import iterative_hypergraph_alignment


def _edges(values):
    edges = []
    for value in values:
        edge = {index(node) for node in value}
        if not edge or min(edge) < 0:
            raise ValueError("Hyperedges must contain nonnegative integer node IDs and must not be empty.")
        edges.append(edge)
    return edges


def align_hypergraphs(source_hyperedges, target_hyperedges, seed_hyperedge_pairs, max_rounds=10):
    """Return a one-to-one source-to-target node mapping; no node seeds are used."""
    max_rounds = index(max_rounds)
    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1.")
    source_edges, target_edges = _edges(source_hyperedges), _edges(target_hyperedges)
    seed_pairs = []
    source_membership = {frozenset(edge) for edge in source_edges}
    target_membership = {frozenset(edge) for edge in target_edges}
    for source_seed, target_seed in seed_hyperedge_pairs:
        source_seed, target_seed = _edges([source_seed, target_seed])
        if frozenset(source_seed) not in source_membership or frozenset(target_seed) not in target_membership:
            raise ValueError("Every seed hyperedge must belong to its corresponding input hypergraph.")
        seed_pairs.append((source_seed, target_seed))
    if not source_edges or not target_edges or not seed_pairs:
        return {}
    source_nodes = set().union(*source_edges)
    target_nodes = set().union(*target_edges)
    return iterative_hypergraph_alignment(
        sorted(source_nodes), target_nodes, source_edges, target_edges, seed_pairs,
        max(source_nodes | target_nodes), iterations=max_rounds,
    )
