import hashlib
from typing import List, Dict, Tuple

def stable_family_ids(cluster_labels: List[int], medoid_idxs: List[int], fingerprints: List[Dict]) -> Dict[int, str]:
    """
    Assign stable TF-XX family IDs to clusters.
    Sort clusters by (family_size desc, medoid_date asc, medoid_content_hash asc).
    """
    # Gather cluster info
    clusters = {}
    for i, label in enumerate(cluster_labels):
        clusters.setdefault(label, []).append(i)
    cluster_info = []
    for label, idxs in clusters.items():
        size = len(idxs)
        medoid_idx = medoid_idxs[label]
        medoid_date = fingerprints[medoid_idx]['date_ny']
        # Medoid content hash (of feature vector, for determinism)
        fv = fingerprints[medoid_idx]['features']
        fv_bytes = str(sorted(fv.items())).encode()
        medoid_hash = hashlib.sha1(fv_bytes).hexdigest()
        cluster_info.append((label, size, medoid_date, medoid_hash, medoid_idx))
    # Sort
    cluster_info.sort(key=lambda x: (-x[1], x[2], x[3]))
    id_map = {}
    for i, (label, *_ ) in enumerate(cluster_info, 1):
        id_map[label] = f"TF-{i:02d}"
    return id_map

def assign_family_ids(labels: List[int], id_map: Dict[int, str], sil_samples: List[float]) -> List[str]:
    assigned = []
    for i, label in enumerate(labels):
        fam = id_map.get(label, None)
        if fam is None or sil_samples[i] < -0.1:
            assigned.append("TF-00")
        else:
            assigned.append(fam)
    return assigned
