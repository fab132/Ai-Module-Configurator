from sqlalchemy.orm import Session
from models.entities import Combo, ComboItem, LoraModel


def get_all(db: Session) -> list[Combo]:
    return db.query(Combo).order_by(Combo.created_at.desc()).all()


def get_by_name(db: Session, name: str) -> Combo | None:
    return db.query(Combo).filter(Combo.name == name).first()


def save(db: Session, name: str, items: list[dict]) -> Combo:
    """
    items: list of {"lora_model_id": int, "slot_index": int, "weight": float}
    If a combo with this name already exists, it is replaced.
    """
    name = name.strip()
    if not name:
        raise ValueError("Combo name cannot be empty")
    existing = db.query(Combo).filter(Combo.name == name).first()
    if existing:
        db.delete(existing)
        db.commit()
    combo = Combo(name=name)
    db.add(combo)
    db.flush()
    for item in items:
        ci = ComboItem(
            combo_id=combo.id,
            lora_model_id=item["lora_model_id"],
            slot_index=item["slot_index"],
            weight=item.get("weight", 1.0),
        )
        db.add(ci)
    db.commit()
    db.refresh(combo)
    return combo


def delete(db: Session, combo_id: int) -> None:
    combo = db.query(Combo).filter(Combo.id == combo_id).first()
    if combo:
        db.delete(combo)
        db.commit()
