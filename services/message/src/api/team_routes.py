from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.team import delete_team, get_team_info, modify_team, create_team, join_team as join_a_team

router = APIRouter(prefix="/team")


@router.get("/{team_id}", response_model=dict)
def get_team(team_id: int):
    try:
        return get_team_info(team_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting team: {str(e)}""")


class TeamCreateRequest(BaseModel):
    team_name: str
    creator_email: str
    org_id: int


@router.post("", response_model=int)
def create_team(request: TeamCreateRequest):
    try:
        return create_team(request.team_name, request.creator_email, request.org_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering team: {str(e)}""")


class TeamEditRequest(BaseModel):
    team_name: str
    current_user_email: str


@router.put("/{team_id}", response_model=bool)
def edit_team(team_id: int, request: TeamEditRequest):
    try:
        return modify_team(team_id, request.current_user_email, request.team_name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying team: {str(e)}""")


@router.delete("/{team_id}", response_model=bool)
def del_team(team_id: int):
    try:
        return delete_team(team_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting team: {str(e)}""")


class TeamJoinRequest(BaseModel):
    team_id: int
    user_email: str


@router.post("/join", response_model=bool)
def join_team(request: TeamJoinRequest):
    try:
        return join_a_team(request.team_id, request.user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error joining team: {str(e)}""")
