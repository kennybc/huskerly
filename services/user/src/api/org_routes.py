from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.user import get_all_users_from_userpool_with_org_id, list_org_requests, request_org, update_org_request, join_org, invite_org

router = APIRouter(prefix="/org")


@router.get("/requests", response_model=List[tuple])
def get_org_requests():
    try:
        requests = list_org_requests()
        return requests
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error sending organization request: {str(e)}""")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


# TODO: all str/int responses should be dict
@router.post("/request", response_model=str)
def request_organization(request: OrgCreateRequest):
    try:
        status = request_org(request.org_name, request.creator_email)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error sending organization request: {str(e)}""")


class OrgApproveRequest(BaseModel):
    org_name: str
    creator_email: str
    current_user_email: str  # TODO: should use session token
    status: str


@router.put("/request", response_model=str)
def update_organization_request(request: OrgApproveRequest):
    try:
        status = update_org_request(
            request.org_name, request.creator_email,
            request.current_user_email, request.status)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error updating organization request: {str(e)}""")


class JoinRequest(BaseModel):
    org_id: int
    user_email: str


@router.post("/join", response_model=str)
def join_organization(request: JoinRequest):
    try:
        org_id = join_org(request.org_id, request.user_email)
        return org_id
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error joining organization: {str(e)}""")


class InviteRequest(BaseModel):
    org_id: int
    invitee_email: str
    inviter_email: str
    lifetime: Optional[int] = 86400


@router.post("/invite", response_model=str)
def invite_to_organization(invite_request: InviteRequest):
    try:
        org_id = invite_org(invite_request.org_id, invite_request.invitee_email,
                            invite_request.inviter_email, invite_request.lifetime)
        return org_id
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error inviting to organization: {str(e)}""")


@router.get("/{org_id}", response_model=List[dict])
def get_all_users(org_id: int):
    try:
        users = get_all_users_from_userpool_with_org_id(org_id)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting all users from organization: {str(e)}""")
