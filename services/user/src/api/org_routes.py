from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from core import user

router = APIRouter(prefix="/org")


@router.get("/requests", response_model=dict, tags=['Public'])
def get_org_requests():
    requests = user.list_org_requests()
    return {'Status': 'SUCCESS', 'Requests': requests}


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("/request", response_model=dict, tags=['Public'])
def request_organization(request: OrgCreateRequest):
    user.request_org(request.org_name, request.creator_email)
    return {'Status': 'SUCCESS'}


class OrgApproveRequest(BaseModel):
    org_name: str
    creator_email: str
    current_user_email: str  # TODO: should use session token
    status: str


@router.put("/request", response_model=dict, tags=['Public'])
def update_organization_request(request: OrgApproveRequest):
    org_id = user.update_org_request(
        request.org_name, request.creator_email,
        request.current_user_email, request.status)
    return {'Status': 'SUCCESS', 'org_id': org_id}


class JoinRequest(BaseModel):
    org_id: int
    user_email: str


@router.post("/join", response_model=dict, tags=['Public'])
def join_organization(request: JoinRequest):
    user.join_org(request.org_id, request.user_email)
    return {'Status': 'SUCCESS'}


class InviteRequest(BaseModel):
    org_id: int
    invitee_email: str
    inviter_email: str
    lifetime: Optional[int] = 86400


@router.post("/invite", response_model=dict, tags=['Public'])
def invite_to_organization(invite_request: InviteRequest):
    user.invite_org(invite_request.org_id, invite_request.invitee_email,
                    invite_request.inviter_email, invite_request.lifetime)
    return {'Status': 'SUCCESS'}


@router.get("/{org_id}", response_model=dict, tags=['Private'])
def get_all_users(org_id: int):
    users = user.get_all_users_from_userpool_with_org_id(org_id)
    return {'Status': 'SUCCESS', 'Users': users}


class PromoteRequest(BaseModel):
    user_email: str
    target_role: str


@router.put("/{org_id}/promote", response_model=dict, tags=['Private'])
def promote_user(org_id: int, request: PromoteRequest):
    user.promote_user(
        org_id, request.user_email, request.target_role)
    return {'Status': 'SUCCESS'}


class DemoteRequest(BaseModel):
    user_email: str


@router.put("/{org_id}/demote", response_model=dict, tags=['Private'])
def demote_user(org_id: int, request: DemoteRequest):
    user.demote_to_member(org_id, request.user_email)
    return {'Status': 'SUCCESS'}
