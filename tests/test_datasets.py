import unittest
from pathlib import Path

from experiments.verify_datasets import verify


class BundledDatasetTests(unittest.TestCase):
    def test_snapshots_and_seed_pools_match_the_manifests(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(verify(root), {
            "verified_snapshots": 16,
            "verified_pairs": 10,
            "bytes": 1732125,
        })


if __name__ == "__main__":
    unittest.main()
