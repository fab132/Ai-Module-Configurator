from sqlalchemy.orm import Session
from models.entities import LoraModel


def get_all(db: Session) -> list[LoraModel]:
    return db.query(LoraModel).order_by(LoraModel.category, LoraModel.name).all()


def add(db: Session, name: str, category: str, file_path: str) -> LoraModel:
    model = LoraModel(name=name.strip(), category=category.strip(), file_path=file_path.strip())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update(db: Session, lora_id: int, name: str, category: str, file_path: str) -> LoraModel:
    model = db.query(LoraModel).filter(LoraModel.id == lora_id).first()
    if not model:
        raise ValueError(f"LoraModel {lora_id} not found")
    model.name = name.strip()
    model.category = category.strip()
    model.file_path = file_path.strip()
    db.commit()
    db.refresh(model)
    return model


def delete(db: Session, lora_id: int) -> None:
    model = db.query(LoraModel).filter(LoraModel.id == lora_id).first()
    if model:
        db.delete(model)
        db.commit()
