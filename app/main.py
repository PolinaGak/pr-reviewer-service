from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import get_db
from .crud import get_stats
from .error_handler import custom_http_exception_handler
from .schemas import ErrorCode, StatsResponse

app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="1.0.0",
)

app.add_exception_handler(HTTPException, custom_http_exception_handler)


@app.post(
    "/team/add", status_code=201, response_model=schemas.TeamResponse, tags=["Teams"]
)
def add_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    try:
        db_team = crud.create_team(db, team)
        return db_team
    except ValueError as e:
        if str(e) == "TEAM_EXISTS":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": ErrorCode.TEAM_EXISTS,
                        "message": "team_name already exists",
                    }
                },
            )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/team/get", response_model=schemas.TeamResponse, tags=["Teams"])
def get_team(team_name: str, db: Session = Depends(get_db)):
    team = crud.get_team(db, team_name)
    if not team:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {"code": ErrorCode.NOT_FOUND, "message": "resource not found"}
            },
        )
    return team


@app.post("/users/setIsActive", response_model=schemas.UserResponse, tags=["Users"])
def set_user_active(data: schemas.UserSetActive, db: Session = Depends(get_db)):
    try:
        user = crud.set_user_active(db, data.user_id, data.is_active)
        return user
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": ErrorCode.NOT_FOUND,
                        "message": "resource not found",
                    }
                },
            )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/getReview", response_model=schemas.UserReviewResponse, tags=["Users"])
def get_user_reviews(user_id: str = Query(...), db: Session = Depends(get_db)):
    prs = crud.get_user_pull_requests(db, user_id)
    return schemas.UserReviewResponse(user_id=user_id, pull_requests=prs)


@app.post(
    "/pullRequest/create",
    status_code=201,
    response_model=schemas.PullRequestResponse,
    tags=["PullRequests"],
)
def create_pull_request(pr: schemas.PullRequestCreate, db: Session = Depends(get_db)):
    try:
        db_pr = crud.create_pr(db, pr)
        return schemas.PullRequestResponse.from_orm(db_pr)
    except ValueError as e:
        if str(e) == "PR_EXISTS":
            raise HTTPException(
                status_code=409,
                detail={
                    "error": {
                        "code": ErrorCode.PR_EXISTS,
                        "message": "PR id already exists",
                    }
                },
            )
        elif str(e) == "NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": ErrorCode.NOT_FOUND,
                        "message": "author/team not found",
                    }
                },
            )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post(
    "/pullRequest/merge",
    response_model=schemas.PullRequestResponse,
    tags=["PullRequests"],
)
def merge_pull_request(data: dict, db: Session = Depends(get_db)):
    pr_id = data.get("pull_request_id")
    if not pr_id:
        raise HTTPException(
            status_code=422, detail="pull_request_id is required in request body"
        )
    db_pr = crud.merge_pr(db, pr_id)
    return schemas.PullRequestResponse.from_orm(db_pr)


@app.post(
    "/pullRequest/reassign",
    response_model=schemas.ReassignResponse,
    tags=["PullRequests"],
)
def reassign_reviewer(data: schemas.ReassignRequest, db: Session = Depends(get_db)):
    try:
        pr, new_id = crud.reassign_reviewer(db, data.pull_request_id, data.old_user_id)
        return schemas.ReassignResponse(
            pr=schemas.PullRequestResponse.from_orm(pr), replaced_by=new_id
        )

    except ValueError as e:
        error_map = {
            "PR_MERGED": (ErrorCode.PR_MERGED, 409, "cannot reassign on merged PR"),
            "NOT_ASSIGNED": (
                ErrorCode.NOT_ASSIGNED,
                409,
                "reviewer is not assigned to this PR",
            ),
            "NO_CANDIDATE": (
                ErrorCode.NO_CANDIDATE,
                409,
                "no active replacement candidate in team",
            ),
            "NOT_FOUND": (ErrorCode.NOT_FOUND, 404, "resource not found"),
        }

        if str(e) in error_map:
            code, status, msg = error_map[str(e)]
            raise HTTPException(
                status_code=status, detail={"error": {"code": code, "message": msg}}
            )

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
def get_statistics(db: Session = Depends(get_db)):
    stats = get_stats(db)
    return stats


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "PR Reviewer Assignment Service"}
