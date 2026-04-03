import json
from sqlalchemy.orm import Session
from services.json_builder import build
from services.file_transfer import send_to_comfyui, save_workflow_file
from services.history_service import log_run
from services import client_service
from models.entities import RunLog


def run(db: Session, params: dict, customer: str, combo_name: str = None,
        send_to_api: bool = True) -> tuple[RunLog, dict]:
    """
    Validate params, optionally look up client profile, build workflow JSON,
    optionally send to ComfyUI, log run. Returns (run_log, workflow_dict).
    """
    # Try to fetch client profile for the person parameter
    client_data = None
    person_name = params.get("person", "")
    if person_name:
        client = client_service.get_by_name(db, person_name)
        if client:
            client_data = {
                "name": client.name,
                "lora_checkpoint": client.lora_checkpoint or "",
                "prompt_prefix": client.prompt_prefix or "",
                "email": client.email or "",
                "notes": client.notes or "",
                "profile_picture": client.profile_picture or "",
            }

    workflow = build(params, client=client_data)

    if send_to_api:
        send_to_comfyui(workflow)

    save_workflow_file(workflow)
    entry = log_run(db, customer=customer or "anonymous", config=workflow, combo_name=combo_name)
    return entry, workflow
