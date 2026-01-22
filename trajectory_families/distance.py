import numpy as np
from typing import List

def dtw_distance(x: np.ndarray, y: np.ndarray) -> float:
    """Compute DTW distance between two 1D arrays (deterministic, no window)."""
    n, m = len(x), len(y)
    dtw = np.full((n+1, m+1), np.inf)
    dtw[0, 0] = 0.0
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(x[i-1] - y[j-1])
            dtw[i, j] = cost + min(dtw[i-1, j],    # insertion
                                   dtw[i, j-1],    # deletion
                                   dtw[i-1, j-1])  # match
    return float(dtw[n, m])

def pairwise_dtw(X: np.ndarray) -> np.ndarray:
    """Compute full pairwise DTW distance matrix for N samples."""
    N = X.shape[0]
    D = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):
            d = dtw_distance(X[i], X[j])
            D[i, j] = D[j, i] = d
    return D
