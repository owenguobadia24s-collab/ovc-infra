import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics import silhouette_score
import random

class PAMClustering:
    def __init__(self, D: np.ndarray, k: int, seed: int = 42):
        self.D = D
        self.k = k
        self.seed = seed
        self.medoids = None
        self.labels = None

    def fit(self):
        np.random.seed(self.seed)
        random.seed(self.seed)
        N = self.D.shape[0]
        # 1. Initialize medoids randomly (deterministic by seed)
        medoids = np.random.choice(N, self.k, replace=False)
        labels = np.argmin(self.D[medoids, :], axis=0)
        changed = True
        while changed:
            changed = False
            for i in range(self.k):
                cluster_idx = np.where(labels == i)[0]
                if len(cluster_idx) == 0:
                    continue
                # Find new medoid for this cluster
                intra_dists = self.D[np.ix_(cluster_idx, cluster_idx)]
                costs = intra_dists.sum(axis=1)
                new_medoid = cluster_idx[np.argmin(costs)]
                if medoids[i] != new_medoid:
                    medoids[i] = new_medoid
                    changed = True
            labels = np.argmin(self.D[medoids, :], axis=0)
        self.medoids = medoids
        self.labels = labels
        return self

    def get_assignments(self):
        return self.labels

    def get_medoids(self):
        return self.medoids

def select_k(D: np.ndarray, X: np.ndarray, k_range=range(5,16), seed=42) -> Tuple[int, np.ndarray, np.ndarray]:
    best_k = None
    best_score = -np.inf
    best_labels = None
    best_medoids = None
    for k in k_range:
        pam = PAMClustering(D, k, seed=seed).fit()
        labels = pam.get_assignments()
        score = silhouette_score(D, labels, metric='precomputed')
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels.copy()
            best_medoids = pam.get_medoids().copy()
    return best_k, best_labels, best_medoids

def compute_silhouette(D: np.ndarray, labels: np.ndarray) -> np.ndarray:
    from sklearn.metrics import silhouette_samples
    return silhouette_samples(D, labels, metric='precomputed')
