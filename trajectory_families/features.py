import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

def load_fingerprints(index_csv: Path, fingerprints_dir: Path) -> List[Dict]:
    """Load fingerprints and metadata from index and JSON files."""
    import csv
    fingerprints = []
    with open(index_csv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fp_path = fingerprints_dir / f"{row['symbol']}_{row['date_ny']}.json"
            with open(fp_path) as jf:
                fp = json.load(jf)
            fp['symbol'] = row['symbol']
            fp['date_ny'] = row['date_ny']
            fingerprints.append(fp)
    return fingerprints

def extract_feature_matrix(fingerprints: List[Dict], feature_keys: List[str]) -> np.ndarray:
    """Extract feature matrix (N x D) from fingerprints."""
    X = np.array([[fp['features'][k] for k in feature_keys] for fp in fingerprints], dtype=float)
    return X

def zscore_standardize(X: np.ndarray) -> np.ndarray:
    """Z-score standardize features (column-wise, stable)."""
    mean = X.mean(axis=0)
    std = X.std(axis=0, ddof=0)
    std[std == 0] = 1.0
    return (X - mean) / std

def get_feature_keys(fingerprints: List[Dict]) -> List[str]:
    """Get ordered feature keys (26-d, spec)."""
    # Assume all fingerprints have same keys, sorted for determinism
    keys = sorted(fingerprints[0]['features'].keys())
    assert len(keys) == 26, f"Expected 26 features, got {len(keys)}"
    return keys
