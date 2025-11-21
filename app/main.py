from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud, schemas

from .database  import get_db

app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="1.0.0",
    openapi_tags=[
        {"name": "Teams"},
        {"name": "Users"},
        {"name": "PullRequests"},
        {"name": "Health"},
    ]
)

@app.post("/team/add", status_code=201, tags=["Teams"])
def add_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    try:
        db_team = crud.create_team(db, team)
        return {"team": db_team}
    except ValueError as e:
        if str(e) == "TEAM_EXISTS":
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "TEAM_EXISTS", "message": "team_name already exists"}}
            )
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/team/get", tags=["Teams"])
def get_team(team_name: str, db: Session = Depends(get_db)):
    team = crud.get_team(db, team_name)
    if not team:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "resource not found"}}
        )
    return team

@app.post("/users/setIsActive", tags=["Users"])
def set_user_active(data: schemas.UserSetActive, db: Session = Depends(get_db)):
    try:
        user = crud.set_user_active(db, data.user_id, data.is_active)
        return {"user": user}
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={"error": {"code": "NOT_FOUND", "message": "resource not found"}}
            )
        raise HTTPException(status_code=500)

@app.get("/users/getReview", tags=["Users"])
def get_user_reviews(user_id: str = Query(...), db: Session = Depends(get_db)):
    prs = crud.get_user_pull_requests(db, user_id)
    return {
        "user_id": user_id,
        "pull_requests": prs
    }

@app.post("/pullRequest/create", status_code=201, tags=["PullRequests"])
def create_pull_request(pr: schemas.PullRequestCreate, db: Session = Depends(get_db)):
    try:
        db_pr = crud.create_pr(db, pr)
        return {"pr": db_pr}
    except ValueError as e:
        if str(e) == "PR_EXISTS":
            raise HTTPException(
                status_code=409,
                detail={"error": {"code": "PR_EXISTS", "message": "PR id already exists"}}
            )
        elif str(e) == "NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={"error": {"code": "NOT_FOUND", "message": "author/team not found"}}
            )
        raise HTTPException(status_code=500)

@app.post("/pullRequest/merge", tags=["PullRequests"])
def merge_pull_request(data: dict, db: Session = Depends(get_db)):
    pr_id = data.get("pull_request_id")
    if not pr_id:
        raise HTTPException(status_code=422, detail="pull_request_id is required")
    try:
        db_pr = crud.merge_pr(db, pr_id)
        return {"pr": db_pr}
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={"error": {"code": "NOT_FOUND", "message": "resource not found"}}
            )
        raise HTTPException(status_code=500)

@app.post("/pullRequest/reassign", tags=["PullRequests"])
def reassign_reviewer(data: schemas.ReassignRequest, db: Session = Depends(get_db)):
    try:
        pr, new_id = crud.reassign_reviewer(db, data.pull_request_id, data.old_user_id)
        return {"pr": pr, "replaced_by": new_id}
    except ValueError as e:
        error_map = {
            "PR_MERGED": ("PR_MERGED", "cannot reassign on merged PR", 409),
            "NOT_ASSIGNED": ("NOT_ASSIGNED", "reviewer is not assigned to this PR", 409),
            "NO_CANDIDATE": ("NO_CANDIDATE", "no active replacement candidate in team", 409),
            "NOT_FOUND": ("NOT_FOUND", "resource not found", 404),
        }
        if str(e) in error_map:
            code, msg, status = error_map[str(e)]
            raise HTTPException(
                status_code=status,
                detail={"error": {"code": code, "message": msg}}
            )
        raise HTTPException(status_code=500)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "PR Reviewer Assignment Service"}
