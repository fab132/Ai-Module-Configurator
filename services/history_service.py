import json
from sqlalchemy.orm import Session
from models.entities import RunLog


def log_run(db: Session, customer: str, config: dict, combo_name: str = None) -> RunLog:
    entry = RunLog(
        customer=customer,
        combo_name=combo_name,
        config_json=json.dumps(config),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_all(db: Session) -> list[RunLog]:
    return db.query(RunLog).order_by(RunLog.ran_at.desc()).all()


def get_by_customer(db: Session, customer: str) -> list[RunLog]:
    return db.query(RunLog).filter(RunLog.customer == customer).order_by(RunLog.ran_at.desc()).all()
