from datetime import datetime
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
    created_at = Column(DateTime, default=datetime.utcnow)

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
    ran_at = Column(DateTime, default=datetime.utcnow)
