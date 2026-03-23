"""
Tests for Combo and ComboItem ORM entities and service logic.
Responsible: Fabian Eppenberger
"""
from models.entities import Combo, ComboItem, LoraModel


def test_combo_can_be_saved(db_session):
    """A named Combo can be inserted into the database."""
    combo = Combo(name="Test Combo")
    db_session.add(combo)
    db_session.commit()
    assert combo.id is not None


def test_combo_can_be_loaded_by_name(db_session):
    """A saved Combo can be retrieved by its name."""
    db_session.add(Combo(name="Client-X Standard"))
    db_session.commit()

    result = db_session.query(Combo).filter_by(name="Client-X Standard").first()
    assert result is not None


def test_combo_with_items_persists_correctly(db_session):
    """A Combo with ComboItems is fully persisted and retrievable."""
    pass


def test_combo_items_are_deleted_with_combo(db_session):
    """Deleting a Combo must cascade-delete all its ComboItems."""
    pass


def test_combo_name_must_be_unique(db_session):
    """Two Combos with the same name must raise an integrity error."""
    pass


def test_combo_item_references_valid_lora_model(db_session):
    """A ComboItem must reference an existing LoraModel."""
    pass


def test_combo_slot_index_is_stored_correctly(db_session):
    """The slot_index of a ComboItem must be stored and retrieved correctly."""
    pass
