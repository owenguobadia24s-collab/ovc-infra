import shutil
from pathlib import Path
from typing import List, Dict

def copy_gallery(fingerprints: List[Dict], assignments: List[str], out_dir: Path):
    """Copy trajectory.png for each day into by_family/TF-XX/ and medoids/ folders."""
    fam_dirs = {}
    for fp, fam in zip(fingerprints, assignments):
        src = Path(fp['trajectory_plot_path'])  # must be absolute or relative to repo
        dest_dir = out_dir / 'by_family' / fam
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{fp['symbol']}_{fp['date_ny']}.png"
        shutil.copy2(src, dest)
        fam_dirs.setdefault(fam, []).append((fp, dest))
    return fam_dirs

def copy_medoids(fingerprints: List[Dict], medoid_idxs: List[int], assignments: List[str], out_dir: Path, id_map: Dict[int, str]):
    """Copy medoid plots to medoids/TF-XX_medoid.png."""
    medoid_dir = out_dir / 'medoids'
    medoid_dir.mkdir(parents=True, exist_ok=True)
    for label, tfid in id_map.items():
        idx = medoid_idxs[label]
        fp = fingerprints[idx]
        src = Path(fp['trajectory_plot_path'])
        dest = medoid_dir / f"{tfid}_medoid.png"
        shutil.copy2(src, dest)
