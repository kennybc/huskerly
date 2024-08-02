from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.organization import delete_org, get_org_info, modify_org, register_org


router = APIRouter(prefix="/org")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("", response_model=int)
def create_org(request: OrgCreateRequest):
    try:
        return register_org(request.org_name, request.creator_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering org: {str(e)}""")


class OrgEditRequest(BaseModel):
    org_name: str
    current_user_email: str
    lead_admin_email: str


@router.put("/{org_id}", response_model=bool)
def edit_org(org_id: int, request: OrgEditRequest):
    try:
        return modify_org(org_id, request.current_user_email, request.org_name, request.lead_admin_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying org: {str(e)}""")


class OrgDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{org_id}", response_model=bool)
def del_org(org_id: int, request: OrgDeleteRequest):
    try:
        return delete_org(org_id, request.current_user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting org: {str(e)}""")


@router.get("/{org_id}", response_model=dict)
def get_org(org_id: int):
    try:
        return get_org_info(org_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting org: {str(e)}""")
