import os

def filename_callback(filename: bytes):
    # 1) Normalize backslashes (Windows-invalid) to forward slashes (git-normal)
    filename = filename.replace(b'\\', b'/')

    # 2) Drop paths with Windows-forbidden characters (rare, but can break tools)
    forbidden = b':*?"<>|'
    if any(ch in filename for ch in forbidden):
        return None

    # 3) Drop leading slash if present (also odd)
    if filename.startswith(b'/'):
        filename = filename.lstrip(b'/')

    return filename