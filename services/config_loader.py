import json
from pathlib import Path

CONFIGS_DIR = Path(__file__).parent.parent / "configs"


def get_options(parameter: str) -> list[str]:
    param_dir = CONFIGS_DIR / parameter
    if not param_dir.exists():
        return []
    return sorted(f.stem for f in param_dir.glob("*.json"))


def load_config(parameter: str, option: str) -> dict:
    config_path = CONFIGS_DIR / parameter / f"{option}.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path) as f:
        return json.load(f)
