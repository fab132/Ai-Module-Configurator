import json
from services.config_loader import load_config
from utils.validators import RunParams

PARAM_KEYS = ["person", "content_type", "platform", "format", "scenery", "outfit", "lighting", "perspective"]


def build(params: dict) -> dict:
    """Validate and merge all 8 parameter configs into one workflow dict."""
    validated = RunParams(**params)  # raises ValidationError if invalid

    workflow = {}
    for key in PARAM_KEYS:
        value = getattr(validated, key)
        config = load_config(key, value)  # raises FileNotFoundError if missing
        workflow[key] = config

    workflow["_meta"] = {
        "person": validated.person,
        "content_type": validated.content_type,
        "platform": validated.platform,
        "format": validated.format,
        "scenery": validated.scenery,
        "outfit": validated.outfit,
        "lighting": validated.lighting,
        "perspective": validated.perspective,
    }
    return workflow
