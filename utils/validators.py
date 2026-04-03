from pydantic import BaseModel, field_validator

PARAM_KEYS = ["person", "content_type", "platform", "format", "scenery", "outfit", "lighting", "perspective"]


class RunParams(BaseModel):
    person: str
    content_type: str
    platform: str
    format: str
    scenery: str
    outfit: str
    lighting: str
    perspective: str

    @field_validator('*')
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("field is required")
        return v


class ComboName(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()


class LoraWeight(BaseModel):
    weight: float

    @field_validator('weight')
    @classmethod
    def valid_range(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")
        return v
