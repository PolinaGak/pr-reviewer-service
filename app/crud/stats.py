from sqlalchemy.orm import Session
from ..models import PullRequest, User


def get_stats(db: Session) -> dict:
    # Пользователи
    all_users = db.query(User).all()
    total_users = len(all_users)
    active_users = sum(1 for u in all_users if u.is_active)
    inactive_users = total_users - active_users

    # PR и статусы
    all_prs = db.query(PullRequest).all()
    total_prs = len(all_prs)
    prs_by_status = {}
    for pr in all_prs:
        prs_by_status[pr.status] = prs_by_status.get(pr.status, 0) + 1

    # Статистика по ревьюерам
    reviewer_counter = {}
    for pr in all_prs:
        for reviewer_id in pr.assigned_reviewers or []:
            reviewer_counter[reviewer_id] = reviewer_counter.get(reviewer_id, 0) + 1

    # Топ-5
    top_reviewers = [
        {"user_id": uid, "assigned_count": cnt}
        for uid, cnt in sorted(
            reviewer_counter.items(), key=lambda x: x[1], reverse=True
        )[:5]
    ]

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_prs": total_prs,
        "prs_by_status": [
            {"status": str(status), "count": count}
            for status, count in prs_by_status.items()
        ],
        "top_reviewers": top_reviewers,
    }