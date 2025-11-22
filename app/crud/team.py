from sqlalchemy.orm import Session, selectinload
from ..models import Team, User
from ..schemas.team import TeamCreate


def get_team(db: Session, team_name: str):
    return (
        db.query(Team)
        .options(selectinload(Team.members))
        .filter(Team.team_name == team_name)
        .first()
    )


def create_team(db: Session, team_data: TeamCreate):
    if get_team(db, team_data.team_name):
        raise ValueError("TEAM_EXISTS")

    db_team = Team(team_name=team_data.team_name)
    db.add(db_team)
    db.flush()

    for member in team_data.members:
        user = db.query(User).filter(User.user_id == member.user_id).first()
        if user:
            user.username = member.username
            user.is_active = member.is_active
            user.team_name = team_data.team_name
        else:
            new_user = User(
                user_id=member.user_id,
                username=member.username,
                is_active=member.is_active,
                team_name=team_data.team_name,
            )
            db.add(new_user)

    db.commit()
    db.refresh(db_team)
    return (
        db.query(Team)
        .options(selectinload(Team.members))
        .filter(Team.team_name == db_team.team_name)
        .first()
    )
