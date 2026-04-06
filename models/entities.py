from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class LoraModel(Base):
    __tablename__ = "lora_models"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    combo_items = relationship("ComboItem", back_populates="lora_model")


class Combo(Base):
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    items = relationship("ComboItem", back_populates="combo", cascade="all, delete-orphan")


class ComboItem(Base):
    __tablename__ = "combo_items"

    id = Column(Integer, primary_key=True)
    combo_id = Column(Integer, ForeignKey("combos.id"), nullable=False)
    lora_model_id = Column(Integer, ForeignKey("lora_models.id"), nullable=False)
    slot_index = Column(Integer, nullable=False)
    weight = Column(Float, default=1.0)

    combo = relationship("Combo", back_populates="items")
    lora_model = relationship("LoraModel", back_populates="combo_items")


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True)
    customer = Column(String, nullable=False)
    combo_name = Column(String)
    config_json = Column(String, nullable=False)
    ran_at = Column(DateTime, default=lambda: datetime.now(UTC))
    status = Column(String, default="pending")          # pending | in_progress | done
    output_file = Column(String)                        # path to generated file
    operator_notes = Column(String, default="")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, default="")
    bio = Column(String, default="")
    role = Column(String, default="Operator")
    profile_picture = Column(String)   # data/profile_pics/...
    cover_picture = Column(String)     # data/profile_covers/...
    user = relationship("User", back_populates="profile")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String)
    profile_picture = Column(String)
    lora_checkpoint = Column(String)
    lora_weight = Column(Float, default=0.8)
    prompt_prefix = Column(String, default="")
    negative_prompt = Column(String, default="")
    notes = Column(String)
    training_status = Column(String, default="none")   # none | ready | training | trained
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    photos = relationship("ClientPhoto", back_populates="client", cascade="all, delete-orphan")


class ClientPhoto(Base):
    __tablename__ = "client_photos"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    file_path = Column(String, nullable=False)
    category = Column(String, default="face")   # face | body | style
    label = Column(String, default="")
    uploaded_at = Column(DateTime, default=lambda: datetime.now(UTC))
    client = relationship("Client", back_populates="photos")
