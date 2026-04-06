import json
from sqlalchemy.orm import Session
from models.entities import RunLog

STATUS_PENDING     = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_DONE        = "done"


def log_run(db: Session, customer: str, config: dict, combo_name: str = None) -> RunLog:
    entry = RunLog(
        customer=customer,
        combo_name=combo_name,
        config_json=json.dumps(config),
        status=STATUS_PENDING,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_all(db: Session) -> list[RunLog]:
    return db.query(RunLog).order_by(RunLog.ran_at.desc()).all()


def get_by_customer(db: Session, customer: str) -> list[RunLog]:
    return db.query(RunLog).filter(RunLog.customer == customer).order_by(RunLog.ran_at.desc()).all()


def get_pending(db: Session) -> list[RunLog]:
    return db.query(RunLog).filter(RunLog.status == STATUS_PENDING).order_by(RunLog.ran_at.asc()).all()


def get_by_status(db: Session, status: str) -> list[RunLog]:
    return db.query(RunLog).filter(RunLog.status == status).order_by(RunLog.ran_at.desc()).all()


def count_pending(db: Session) -> int:
    return db.query(RunLog).filter(RunLog.status == STATUS_PENDING).count()


def set_status(db: Session, run_id: int, status: str, operator_notes: str = None) -> RunLog:
    entry = db.query(RunLog).filter(RunLog.id == run_id).first()
    if not entry:
        raise ValueError(f"RunLog {run_id} not found")
    entry.status = status
    if operator_notes is not None:
        entry.operator_notes = operator_notes
    db.commit()
    db.refresh(entry)
    return entry


def set_output(db: Session, run_id: int, output_file: str) -> RunLog:
    entry = db.query(RunLog).filter(RunLog.id == run_id).first()
    if not entry:
        raise ValueError(f"RunLog {run_id} not found")
    entry.output_file = output_file
    entry.status = STATUS_DONE
    db.commit()
    db.refresh(entry)
    return entry
