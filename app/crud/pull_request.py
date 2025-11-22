import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.pull_request import PRStatus, PullRequest
from ..models.user import User


def get_pr(db: Session, pr_id: str):
    return db.query(PullRequest).filter(PullRequest.pull_request_id == pr_id).first()


def _select_reviewers(db: Session, author_id: str, team_name: str):
    candidates = (
        db.query(User)
        .filter(
            User.team_name == team_name,
            User.user_id != author_id,
            User.is_active,
        )
        .all()
    )
    candidates = sorted(candidates, key=lambda u: u.user_id)
    return [u.user_id for u in candidates[:2]]


def create_pr(db: Session, pr_data):
    author = db.query(User).filter(User.user_id == pr_data.author_id).first()
    if not author:
        raise ValueError("NOT_FOUND")

    if get_pr(db, pr_data.pull_request_id):
        raise ValueError("PR_EXISTS")

    reviewers = _select_reviewers(db, pr_data.author_id, author.team_name)

    db_pr = PullRequest(
        pull_request_id=pr_data.pull_request_id,
        pull_request_name=pr_data.pull_request_name,
        author_id=pr_data.author_id,
        assigned_reviewers=reviewers,
        status=PRStatus.OPEN,
    )
    db.add(db_pr)
    db.commit()
    db.refresh(db_pr)
    return db_pr


def merge_pr(db: Session, pr_id: str):
    pr = get_pr(db, pr_id)
    if not pr:
        raise ValueError("NOT_FOUND")
    if pr.status != PRStatus.MERGED:
        pr.status = PRStatus.MERGED
        pr.merged_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(pr)
    return pr


def reassign_reviewer(db: Session, pr_id: str, old_user_id: str):
    pr = get_pr(db, pr_id)
    if not pr:
        raise ValueError("NOT_FOUND")
    if pr.status == PRStatus.MERGED:
        raise ValueError("PR_MERGED")
    if old_user_id not in pr.assigned_reviewers:
        raise ValueError("NOT_ASSIGNED")

    old_user = db.query(User).filter(User.user_id == old_user_id).first()
    if not old_user:
        raise ValueError("NOT_FOUND")

    exclude = set(pr.assigned_reviewers + [pr.author_id])
    candidates = (
        db.query(User)
        .filter(
            User.team_name == old_user.team_name,
            User.is_active,
            ~User.user_id.in_(exclude),
        )
        .all()
    )

    if not candidates:
        raise ValueError("NO_CANDIDATE")

    new_reviewer = random.choice(candidates)
    new_reviewers = [
        new_reviewer.user_id if r == old_user_id else r for r in pr.assigned_reviewers
    ]

    pr.assigned_reviewers = new_reviewers
    db.commit()
    db.refresh(pr)
    return pr, new_reviewer.user_id
