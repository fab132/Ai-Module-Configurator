from sqlalchemy.orm import Session
from models.entities import User, UserProfile


def get_or_create(db: Session, email: str) -> UserProfile:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError(f"User {email} not found")
    if not user.profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return user.profile


def update(db: Session, email: str, full_name: str = None, bio: str = None,
           role: str = None, profile_picture: str = None, cover_picture: str = None) -> UserProfile:
    profile = get_or_create(db, email)
    if full_name is not None:
        profile.full_name = full_name.strip()
    if bio is not None:
        profile.bio = bio.strip()
    if role is not None:
        profile.role = role.strip()
    if profile_picture is not None:
        profile.profile_picture = profile_picture
    if cover_picture is not None:
        profile.cover_picture = cover_picture
    db.commit()
    db.refresh(profile)
    return profile
