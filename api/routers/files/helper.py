import os


def get_file_size_mb(file_path) -> float:
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / 1024 / 1024
    return float("{:.2f}".format(size_mb))
