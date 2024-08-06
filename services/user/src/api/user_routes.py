from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from core import user

router = APIRouter()


def get_session_token(session_token: str = Header(...)):
    if not session_token:
        raise HTTPException(status_code=400, detail="Session token missing")
    # TODO: add logic to validate the session token here
    return session_token


@router.get("/permission/{user_email}", response_model=dict, tags=['Public']) #TODO: should this be public??
def get_permission(user_email):
    permission = user.get_user_permission_level(user_email)
    return {'Status': 'SUCCESS', 'Permission': permission}


@router.get("/permission/{user_email}/{org_id}", response_model=dict, tags=['Public']) #TODO: should this be public??
# TODO: should use session token
def get_permission(user_email: str, org_id: int):
    permission = user.get_user_permission_level(user_email, org_id)
    return {'Status': 'SUCCESS', 'Permission': permission}


@router.get("/invites/{user_email}", response_model=dict, tags=['Public'])
def list_user_invites(user_email: str):
    invites = user.list_invites(user_email)
    return {'Status': 'SUCCESS', 'Invites': invites}
