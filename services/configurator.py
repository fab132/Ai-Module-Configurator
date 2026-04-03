import json
from sqlalchemy.orm import Session
from services.json_builder import build
from services.file_transfer import send_to_comfyui, save_workflow_file
from services.history_service import log_run
from models.entities import RunLog


def run(db: Session, params: dict, customer: str, combo_name: str = None, send_to_api: bool = True) -> tuple[RunLog, dict]:
    """
    Validate params, build workflow JSON, optionally send to ComfyUI, log run.
    Returns (run_log, workflow_dict).
    Raises ValidationError if params invalid, FileNotFoundError if config missing,
    requests.exceptions.RequestException if ComfyUI unreachable (only if send_to_api=True).
    """
    workflow = build(params)  # raises on invalid/missing

    if send_to_api:
        send_to_comfyui(workflow)

    save_workflow_file(workflow)
    entry = log_run(db, customer=customer or "anonymous", config=workflow, combo_name=combo_name)
    return entry, workflow
