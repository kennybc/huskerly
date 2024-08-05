from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core import user

router = APIRouter()


def get_session_token(session_token: str = Header(...)):
    if not session_token:
        raise HTTPException(status_code=400, detail="Session token missing")
    # TODO: add logic to validate the session token here
    return session_token


# @router.get("/users/{user_email}", response_model=dict)
# # TODO: use session token , session_token: str = Depends(get_session_token)
# def get_user(user_email: str):
#     try:
#         user = get_user_from_userpool(user_email)
#         return user
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"""Error getting user information: {str(e)}""")


@router.get("/permission/{user_email}", response_model=dict)
def get_permission(user_email):
    # try:
    permission = user.get_user_permission_level(user_email)
    return {'Status': 'SUCCESS', 'Permission': permission}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error authenticating user permissions: {str(e)}""")


@router.get("/permission/{user_email}/{org_id}", response_model=dict)
# TODO: should use session token
def get_permission(user_email: str, org_id: int):
    # try:
    permission = user.get_user_permission_level(user_email, org_id)
    return {'Status': 'SUCCESS', 'Permission': permission}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"""Error authenticating user permissions: {str(e)}""")


@router.get("/invites/{user_email}", response_model=dict)
def list_user_invites(user_email: str):
    # try:
    invites = user.list_invites(user_email)
    return {'Status': 'SUCCESS', 'Invites': invites}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"""Error fetching invites for user {
    #                         user_email}: {str(e)}""")
