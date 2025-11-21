from .config import settings
from fastapi import FastAPI
#from .api import teams, users, pull_requests, health
from .database import engine
from .models import base

app = FastAPI(title="PR Reviewer Assignment Service", version="1.0.0")

#app.include_router(teams.router)
#app.include_router(users.router)
#app.include_router(pull_requests.router)
#app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "PR Reviewer Assignment Service (Fall 2025)"}
