"""Check the released numeric evidence using only the Python standard library."""
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def rows(path):
    with (HERE / path).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def groups(records, keys):
    result = defaultdict(list)
    for record in records:
        result[tuple(record[key] for key in keys)].append(record)
    return result


def close(actual, expected, label):
    assert math.isfinite(float(actual)) and math.isfinite(float(expected)), label
    assert math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=1e-9), (label, actual, expected)


def verify_runs(records, key, repetitions):
    assert len({tuple(row[k] for k in key + ['run_idx']) for row in records}) == len(records)
    for cell, cell_rows in groups(records, key).items():
        assert len(cell_rows) == repetitions, cell
        assert {int(row['run_idx']) for row in cell_rows} == set(range(repetitions)), cell
    for row in records:
        assert int(row['run_seed']) == 42 + int(row['run_idx'])
        correct, predicted, truth = [float(row[k]) for k in ['correct_matches', 'predicted_matches', 'ground_truth_total']]
        assert 0 <= correct <= min(predicted, truth)
        for metric, expected in [('precision', correct / predicted if predicted else 0),
                                 ('recall', correct / truth if truth else 0),
                                 ('f1', 2 * correct / (predicted + truth) if predicted + truth else 0)]:
            assert 0 <= float(row[metric]) <= 1
            close(row[metric], expected, (key, metric, row['run_idx']))


def verify_summary(records, summaries, key):
    cells = groups(records, key)
    assert len(summaries) == len(cells) * 3
    for row in summaries:
        selected = cells[tuple(row[k] for k in key)]
        values = [float(r[row['metric']]) for r in selected]
        close(row['mean'], statistics.mean(values), ('mean', key, row))
        close(row['sample_sd'], statistics.stdev(values), ('sample_sd', key, row))
        assert int(row['runs']) == len(values)


def quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def main():
    main_runs = rows('main_accuracy/runs.csv')
    assert len(main_runs) == 7500
    verify_runs(main_runs, ['pair_id', 'alpha', 'algorithm'], 50)
    main_summary = rows('main_accuracy/summary.csv')
    verify_summary(main_runs, main_summary, ['dataset', 'pair_id', 'alpha', 'algorithm'])

    ablation = rows('ablation/runs.csv')
    assert len(ablation) == 4000
    verify_runs(ablation, ['pair_id', 'alpha', 'variant'], 50)
    grouped = groups(ablation, ['dataset', 'alpha', 'variant', 'run_idx'])
    run_level = rows('ablation/run_level_pair_means.csv')
    assert len(run_level) == len(grouped) == 2000
    for row in run_level:
        pair = grouped[tuple(row[k] for k in ['dataset', 'alpha', 'variant', 'run_idx'])]
        assert len(pair) == 2 and len({r['pair_id'] for r in pair}) == 2
        for metric in ['precision', 'recall', 'f1']:
            close(row[metric], statistics.mean(float(r[metric]) for r in pair), ('pair means', row))
    verify_summary(run_level, rows('ablation/figure_source_data.csv'), ['dataset', 'alpha', 'variant'])
    for cell in groups(ablation, ['pair_id', 'alpha', 'run_idx']).values():
        assert len(cell) == 2 and cell[0]['seed_hyperedge_fingerprint'] == cell[1]['seed_hyperedge_fingerprint']
    main_index = {(r['pair_id'], r['alpha'], r['run_idx']): r for r in main_runs if r['algorithm'] == 'ISHA'}
    for row in ablation:
        key = row['pair_id'], row['alpha'], row['run_idx']
        if row['variant'] == 'ISHA' and key in main_index:
            for metric in ['precision', 'recall', 'f1']:
                close(row[metric], main_index[key][metric], ('main versus ablation', key, metric))

    efficiency = rows('efficiency/runs.csv')
    assert len(efficiency) == 400 and all(r['status'] == 'success' for r in efficiency)
    assert {r['dataset_family'] for r in efficiency} == {'tags-stack-overflow', 'threads-ask-ubuntu'}
    assert {r['algorithm'] for r in efficiency} == {'FRUI', 'MAH', 'MAHA', 'ISHA'}
    for row in efficiency:
        row['run_idx'] = row['repeat']
    verify_runs(efficiency, ['dataset_family', 'scale_nodes', 'algorithm'], 10)
    efficiency_summary = rows('efficiency/accuracy_summary.csv')
    verify_summary(efficiency, efficiency_summary, ['dataset_family', 'scale_nodes', 'algorithm'])
    cells = groups(efficiency, ['dataset_family', 'scale_nodes', 'algorithm'])
    for row in rows('efficiency/figure_source_data.csv'):
        selected = cells[tuple(row[k] for k in ['dataset_family', 'scale_nodes', 'algorithm'])]
        column = 'end_to_end_sec' if row['metric'] == 'time_sec' else 'peak_rss_mb'
        values = [float(r[column]) for r in selected]
        close(row['median'], statistics.median(values), ('median', row))
        close(row['q25'], quantile(values, .25), ('q25', row))
        close(row['q75'], quantile(values, .75), ('q75', row))
        assert int(row['successful_runs']) == len(values) == 10

    main_index = {(r['pair_id'], r['alpha'], r['algorithm']): r for r in main_summary if r['metric'] == 'f1'}
    eff_index = {(r['dataset_family'], r['scale_nodes'], r['algorithm']): r for r in efficiency_summary if r['metric'] == 'f1'}
    display_families = {'Tags-Stack-Overflow': 'tags-stack-overflow', 'Threads-Ask-Ubuntu': 'threads-ask-ubuntu'}
    targets = rows('tables/manuscript_f1_targets.csv')
    assert len(targets) == 190
    for row in targets:
        if row['table'] == 'tab:real_alignment_results':
            actual = main_index[(row['pair_id'], row['alpha'], row['algorithm'])]
        else:
            actual = eff_index[(display_families[row['dataset']], row['scale_nodes'], row['algorithm'])]
        for metric in ['mean', 'sample_sd']:
            assert f'{float(actual[metric]):.3f}' == row[metric], (row, actual)

    for record in rows('tables/alignment_dataset_statistics.csv'):
        with (ROOT / 'experiments/pairs_10_real.csv').open(encoding='utf-8', newline='') as handle:
            pair = next(r for r in csv.DictReader(handle) if Path(r['source']).stem + '_vs_' + Path(r['target']).stem == record['pair_id'])
        edge_lists = [[frozenset(map(int, line.split())) for line in (ROOT / pair[k]).read_text().splitlines() if line.strip()] for k in ['source', 'target']]
        nodes = [set().union(*edges) for edges in edge_lists]
        actual = {'source_nodes': len(nodes[0]), 'target_nodes': len(nodes[1]),
                  'source_hyperedges': len(edge_lists[0]), 'target_hyperedges': len(edge_lists[1]),
                  'shared_nodes': len(nodes[0] & nodes[1]),
                  'identical_hyperedges': len(set(edge_lists[0]) & set(edge_lists[1]))}
        assert all(int(record[k]) == v for k, v in actual.items()), record['pair_id']

    verification = json.loads((HERE / 'verification.json').read_text())
    full_dataset_rows = rows('tables/efficiency_full_dataset_statistics.csv')
    full_reference = {r['dataset']: r for r in verification['full_dataset_table_reference']['datasets']}
    assert {r['dataset'] for r in full_dataset_rows} == set(full_reference)
    for record in full_dataset_rows:
        expected = full_reference[record['dataset']]
        for column in ['nodes', 'events', 'distinct_hyperedges']:
            assert int(record[column]) == expected[column], (record['dataset'], column)
    assert verification['result'] == 'passed'
    assert all(item['passed'] for item in verification['checks'])

    manifest_path = HERE / 'file_manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for item in manifest['files']:
            path = HERE / item['path']
            assert path.stat().st_size == item['bytes'], item['path']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], item['path']
    print('PASS: 7,500 main runs, 4,000 ablation runs, 400 efficiency runs;')
    print('190 manuscript mean/SD cells; both figure-source tables;')
    print('10 input-pair statistics; 2 full-dataset statistics; file hashes.')


if __name__ == '__main__':
    main()
