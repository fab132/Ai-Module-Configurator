from sqlalchemy.orm import Session
from models.entities import User, UserProfile, Client
from utils.password_utils import hash_password, verify_password


def register(db: Session, email: str, password: str, role: str = "Operator") -> User:
    if db.query(User).filter(User.email == email).first():
        raise ValueError("Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.flush()  # get user.id without committing

    profile = UserProfile(user_id=user.id, role=role)
    db.add(profile)

    if role == "Customer":
        # Auto-create a Client record for this customer if not already there
        existing_client = db.query(Client).filter(Client.email == email).first()
        if not existing_client:
            name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
            client = Client(name=name, email=email, prompt_prefix="")
            db.add(client)

    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")
    return user


def get_role(db: Session, email: str) -> str:
    """Returns the role for the given email. Defaults to 'Operator'."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return "Operator"
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        return "Operator"
    return profile.role or "Operator"
