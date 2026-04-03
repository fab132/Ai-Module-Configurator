import shutil
from pathlib import Path


def download_local(source: str, destination: str) -> Path:
    src = Path(source)
    dst = Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def save_to_cloud(source: str, bucket: str, key: str) -> str:
    """Upload a file to cloud storage. Returns the remote URI."""
    import boto3
    s3 = boto3.client("s3")
    s3.upload_file(source, bucket, key)
    return f"s3://{bucket}/{key}"
