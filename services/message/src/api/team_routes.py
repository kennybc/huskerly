from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core import team

router = APIRouter(prefix="/team")


@router.get("/{team_id}", response_model=dict)
def get_team(team_id: int):
    try:
        return team.get_team(team_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting team: {str(e)}""")


class TeamCreateRequest(BaseModel):
    team_name: str
    creator_email: str
    org_id: int


@router.post("", response_model=dict)
def create_team(request: TeamCreateRequest):
    try:
        team_id = create_team(
            request.team_name, request.creator_email, request.org_id)
        return {'status': 'SUCCESS', "team_id": team_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering team: {str(e)}""")


class TeamEditRequest(BaseModel):
    team_name: str
    current_user_email: str


@router.put("/{team_id}", response_model=dict)
def edit_team(team_id: int, request: TeamEditRequest):
    try:
        res = team.edit_team(
            team_id, request.current_user_email, request.team_name)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying team: {str(e)}""")


class TeamDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{team_id}", response_model=dict)
def delete_team(team_id: int, request: TeamDeleteRequest):
    try:
        res = team.delete_team(request.current_user_email, team_id)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting team: {str(e)}""")


class TeamJoinRequest(BaseModel):
    team_id: int
    user_email: str


@router.post("/join", response_model=dict)
def join_team(request: TeamJoinRequest):
    try:
        res = team.join_team(request.team_id, request.user_email)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error joining team: {str(e)}""")
