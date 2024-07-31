from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.user import get_all_users_from_userpool, get_user_from_userpool, get_user_permission_level, request_org, update_org_request, list_invites, join_org, invite_org

router = APIRouter()


def get_session_token(session_token: str = Header(...)):
    if not session_token:
        raise HTTPException(status_code=400, detail="Session token missing")
    # TODO: add logic to validate the session token here
    return session_token


@router.get("/users", response_model=List[dict])
def get_all_users():
    try:
        users = get_all_users_from_userpool()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting all users: {str(e)}")


class UserRequest(BaseModel):
    user_email: str


@router.get("/users/{user_email}", response_model=dict)
# TODO: use session token , session_token: str = Depends(get_session_token)
def get_user(request: UserRequest):
    try:
        user = get_user_from_userpool(request.user_email)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting user information: {str(e)}")


class PermissionRequest(BaseModel):
    org_id: Optional[int] = None


@router.get("/users/{user_email}/permission", response_model=str)
# TODO: should use session token
def get_permission(user_email: str, request: PermissionRequest):
    try:
        permission = get_user_permission_level(user_email, request.org_id)
        return permission
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error authenticating user permissions: {str(e)}")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("/org/request", response_model=str)
def request_organization(request: OrgCreateRequest):
    try:
        status = request_org(request.org_name, request.creator_email)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error sending organization request: {str(e)}")


class OrgApproveRequest(BaseModel):
    org_name: str
    current_user_email: str  # TODO: should use session token
    status: str


@router.put("/org/request", response_model=str)
def update_organization_request(request: OrgApproveRequest):
    try:
        status = update_org_request(
            request.org_name, request.current_user_email, request.status)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating organization request: {str(e)}")


@router.get("/invites/{user_email}", response_model=List[dict])
def list_user_invites(user_email: str):
    try:
        invites = list_invites(user_email)
        return invites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching invites for user {
                            user_email}: {str(e)}")


class JoinRequest(BaseModel):
    org_id: int
    user_email: str


@router.post("/org/join", response_model=int)
def join_organization(request: JoinRequest):
    try:
        org_id = join_org(request.org_id, request.user_email)
        return org_id
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error joining organization: {str(e)}")


class InviteRequest(BaseModel):
    org_id: int
    invitee_email: str
    inviter_email: str
    lifetime: Optional[int] = 86400


@router.post("/org/invite", response_model=int)
def invite_to_organization(invite_request: InviteRequest):
    try:
        org_id = invite_org(invite_request.org_id, invite_request.invitee_email,
                            invite_request.inviter_email, invite_request.lifetime)
        return org_id
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error inviting to organization: {str(e)}")
