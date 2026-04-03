import json
import os
import requests
from pathlib import Path

COMFYUI_HOST = os.getenv("COMFYUI_HOST", "127.0.0.1")
COMFYUI_PORT = int(os.getenv("COMFYUI_PORT", 8188))


def send_to_comfyui(workflow: dict) -> dict:
    """POST workflow to ComfyUI /prompt endpoint. Returns API response dict."""
    url = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}/prompt"
    payload = {"prompt": workflow}
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def save_workflow_file(workflow: dict, output_dir: str = "data/workflows") -> Path:
    """Save workflow JSON to disk (for inspection/debugging)."""
    import uuid
    from datetime import datetime
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    filename = out / f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
    with open(filename, "w") as f:
        json.dump(workflow, f, indent=2)
    return filename
