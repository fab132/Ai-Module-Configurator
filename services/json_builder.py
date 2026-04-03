import json
from services.config_loader import load_config
from utils.validators import RunParams

PARAM_KEYS = ["person", "content_type", "platform", "format", "scenery", "outfit", "lighting", "perspective"]


def build(params: dict, client: dict = None) -> dict:
    """
    Validate and merge all 8 parameter configs into one workflow dict.
    If client dict is provided, it is used for the 'person' key instead of loading from file.
    """
    validated = RunParams(**params)

    workflow = {}
    for key in PARAM_KEYS:
        if key == "person" and client:
            workflow[key] = client
        else:
            value = getattr(validated, key)
            config = load_config(key, value)
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
