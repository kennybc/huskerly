from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from core import user

router = APIRouter(prefix="/org")


@router.get("/requests", response_model=dict)
def get_org_requests():
    # try:
    requests = user.list_org_requests()
    return {'Status': 'SUCCESS', 'Requests': requests}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error sending organization request: {str(e)}""")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("/request", response_model=dict)
def request_organization(request: OrgCreateRequest):
    # try:
    user.request_org(request.org_name, request.creator_email)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error sending organization request: {str(e)}""")


class OrgApproveRequest(BaseModel):
    org_name: str
    creator_email: str
    current_user_email: str  # TODO: should use session token
    status: str


@router.put("/request", response_model=dict)
def update_organization_request(request: OrgApproveRequest):
    # try:
    user.update_org_request(
        request.org_name, request.creator_email,
        request.current_user_email, request.status)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error updating organization request: {str(e)}""")


class JoinRequest(BaseModel):
    org_id: int
    user_email: str


@router.post("/join", response_model=dict)
def join_organization(request: JoinRequest):
    # try:
    user.join_org(request.org_id, request.user_email)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error joining organization: {str(e)}""")


class InviteRequest(BaseModel):
    org_id: int
    invitee_email: str
    inviter_email: str
    lifetime: Optional[int] = 86400


@router.post("/invite", response_model=dict)
def invite_to_organization(invite_request: InviteRequest):
    # try:
    user.invite_org(invite_request.org_id, invite_request.invitee_email,
                    invite_request.inviter_email, invite_request.lifetime)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error inviting to organization: {str(e)}""")


@router.get("/{org_id}", response_model=dict)
def get_all_users(org_id: int):
    # try:
    users = user.get_all_users_from_userpool_with_org_id(org_id)
    return {'Status': 'SUCCESS', 'Users': users}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error getting all users from organization: {str(e)}""")


class PromoteRequest(BaseModel):
    user_email: str
    target_role: str


@router.put("/{org_id}/promote", response_model=dict)
def promote_user(org_id: int, request: PromoteRequest):
    # try:
    user.promote_user(
        org_id, request.user_email, request.target_role)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error promoting user: {str(e)}""")


class DemoteRequest(BaseModel):
    user_email: str


@router.put("/{org_id}/demote", response_model=dict)
def demote_user(org_id: int, request: DemoteRequest):
    # try:
    user.demote_to_member(org_id, request.user_email)
    return {'Status': 'SUCCESS'}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error demoting user to member: {str(e)}""")
