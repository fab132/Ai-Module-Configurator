from sqlalchemy.orm import Session
from models.entities import Client, ClientPhoto


def get_all(db: Session) -> list[Client]:
    return db.query(Client).order_by(Client.name).all()


def get_by_name(db: Session, name: str) -> Client | None:
    return db.query(Client).filter(Client.name == name).first()


def get_by_id(db: Session, client_id: int) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def add(db: Session, name: str, email: str = None, lora_checkpoint: str = None,
        prompt_prefix: str = "", notes: str = None, profile_picture: str = None) -> Client:
    client = Client(
        name=name.strip(),
        email=email.strip() if email else None,
        lora_checkpoint=lora_checkpoint.strip() if lora_checkpoint else None,
        prompt_prefix=prompt_prefix.strip() if prompt_prefix else "",
        notes=notes.strip() if notes else None,
        profile_picture=profile_picture,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update(db: Session, client_id: int, name: str, email: str = None,
           lora_checkpoint: str = None, prompt_prefix: str = "",
           notes: str = None, profile_picture: str = None,
           lora_weight: float = None, negative_prompt: str = None) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise ValueError(f"Client {client_id} not found")
    client.name = name.strip()
    client.email = email.strip() if email else None
    client.lora_checkpoint = lora_checkpoint.strip() if lora_checkpoint else None
    client.prompt_prefix = prompt_prefix.strip() if prompt_prefix else ""
    client.notes = notes.strip() if notes else None
    if profile_picture is not None:
        client.profile_picture = profile_picture
    if lora_weight is not None:
        client.lora_weight = lora_weight
    if negative_prompt is not None:
        client.negative_prompt = negative_prompt.strip()
    db.commit()
    db.refresh(client)
    return client


def delete(db: Session, client_id: int) -> None:
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()


# ── Photo management ──────────────────────────────────────────────────────────

def add_photo(db: Session, client_id: int, file_path: str,
              category: str = "face", label: str = "") -> ClientPhoto:
    photo = ClientPhoto(
        client_id=client_id,
        file_path=file_path,
        category=category,
        label=label,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def get_photos(db: Session, client_id: int, category: str = None) -> list[ClientPhoto]:
    q = db.query(ClientPhoto).filter(ClientPhoto.client_id == client_id)
    if category:
        q = q.filter(ClientPhoto.category == category)
    return q.order_by(ClientPhoto.uploaded_at).all()


def delete_photo(db: Session, photo_id: int) -> None:
    photo = db.query(ClientPhoto).filter(ClientPhoto.id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
