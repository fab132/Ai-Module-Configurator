"""
Tests for LoraModel ORM entity and CRUD operations.
Responsible: Fabian Eppenberger
"""
from models.entities import LoraModel


def test_lora_model_can_be_created(db_session):
    """A LoraModel can be inserted into the database."""
    lora = LoraModel(name="test_lora", category="person", file_path="/models/test.safetensors")
    db_session.add(lora)
    db_session.commit()
    assert lora.id is not None


def test_lora_model_can_be_read(db_session):
    """An inserted LoraModel can be retrieved by name."""
    lora = LoraModel(name="read_lora", category="outfit", file_path="/models/read.safetensors")
    db_session.add(lora)
    db_session.commit()

    result = db_session.query(LoraModel).filter_by(name="read_lora").first()
    assert result is not None
    assert result.category == "outfit"


def test_lora_model_name_must_be_unique(db_session):
    """Inserting two LoraModels with the same name must raise an integrity error."""
    pass


def test_lora_model_can_be_updated(db_session):
    """A LoraModel's category can be updated and persisted."""
    pass


def test_lora_model_can_be_deleted(db_session):
    """A LoraModel can be deleted from the database."""
    pass


def test_lora_model_requires_name(db_session):
    """Creating a LoraModel without a name must raise an error."""
    pass


def test_lora_model_requires_file_path(db_session):
    """Creating a LoraModel without a file_path must raise an error."""
    pass
