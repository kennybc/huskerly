from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core import team

router = APIRouter(prefix="/team")


@router.get("/{team_id}", response_model=dict, tags=['Public'])
def get_team(team_id: int):
    team_data = team.get_team(team_id)
    return {'Status': 'SUCCESS', 'Data': team_data}


class TeamCreateRequest(BaseModel):
    team_name: str
    creator_email: str
    org_id: int


@router.post("", response_model=dict, tags=['Public'])
def create_team(request: TeamCreateRequest):
    team_id = team.create_team(
        request.team_name, request.creator_email, request.org_id)
    return {'Status': 'SUCCESS', "team_id": team_id}


class TeamEditRequest(BaseModel):
    team_name: str
    current_user_email: str


@router.put("/{team_id}", response_model=dict, tags=['Public'])
def edit_team(team_id: int, request: TeamEditRequest):
    team.edit_team(
        team_id, request.current_user_email, request.team_name)
    return {'Status': 'SUCCESS'}


class TeamDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{team_id}", response_model=dict, tags=['Public'])
def delete_team(team_id: int, request: TeamDeleteRequest):
    team.delete_team(request.current_user_email, team_id)
    return {'Status': 'SUCCESS'}


class TeamJoinRequest(BaseModel):
    team_id: int
    user_email: str


@router.post("/join", response_model=dict, tags=['Public'])
def join_team(request: TeamJoinRequest):
    team.join_team(request.team_id, request.user_email)
    return {'Status': 'SUCCESS'}

class TeamLeaveRequest(BaseModel):
    team_id: int
    current_user_email: str
    team_user_email: str

@router.post("/leave", response_model=dict, tags=['Public'])
def leave_team(request: TeamLeaveRequest):
    team.leave_team(request.team_id, request.current_user_email, request.team_user_email)
    return {'Status': 'SUCCESS'}
