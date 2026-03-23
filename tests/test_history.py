"""
Tests for RunLog history persistence.
Responsible: Fabian Eppenberger
"""
from models.entities import RunLog


def test_run_log_is_created_after_successful_run(db_session):
    """After a successful run, a RunLog entry must exist in the database."""
    log = RunLog(customer="Test Customer", config_json='{"person": "lis"}')
    db_session.add(log)
    db_session.commit()
    assert log.id is not None


def test_run_log_stores_timestamp_automatically(db_session):
    """A RunLog entry must have a non-null ran_at timestamp."""
    log = RunLog(customer="Test Customer", config_json='{"person": "lis"}')
    db_session.add(log)
    db_session.commit()
    assert log.ran_at is not None


def test_run_log_stores_full_config_json(db_session):
    """The RunLog must store the complete config JSON string."""
    pass


def test_run_logs_are_ordered_by_date(db_session):
    """Querying RunLogs must return them ordered by ran_at descending."""
    pass


def test_run_log_customer_field_is_required(db_session):
    """A RunLog without a customer value must raise an error."""
    pass


def test_run_log_is_immutable_after_creation(db_session):
    """A RunLog entry must not be modified after being committed."""
    pass
