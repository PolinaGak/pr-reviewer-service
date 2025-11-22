from sqlalchemy.orm import Session

from ..models.pull_request import PullRequest
from ..models.user import User


def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def set_user_active(db: Session, user_id: str, is_active: bool):
    user = get_user(db, user_id)
    if not user:
        raise ValueError("NOT_FOUND")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def get_user_pull_requests(db: Session, user_id: str):
    return (
        db.query(PullRequest)
        .filter(PullRequest.assigned_reviewers.contains([user_id]))
        .all()
    )
