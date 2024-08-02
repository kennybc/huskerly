from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core import organization


router = APIRouter(prefix="/org")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("", response_model=int)
def create_org(request: OrgCreateRequest):
    try:
        return organization.create_org(request.org_name, request.creator_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering org: {str(e)}""")


class TransferOrgRequest(BaseModel):
    lead_admin_email: str
    current_user_email: str


@router.put("/{org_id}/transfer", response_model=bool)
def transfer_lead_admin(org_id: int, request: TransferOrgRequest):
    try:
        return organization.transfer_lead_admin(
            org_id, request.lead_admin_email, request.current_user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error transferring org: {str(e)}""")


class OrgEditRequest(BaseModel):
    org_name: str
    current_user_email: str


@router.put("/{org_id}", response_model=bool)
def edit_org(org_id: int, request: OrgEditRequest):
    try:
        return organization.edit_org(org_id, request.current_user_email, request.org_name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying org: {str(e)}""")


class OrgDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{org_id}", response_model=bool)
def delete_org(org_id: int, request: OrgDeleteRequest):
    try:
        return organization.delete_org(org_id, request.current_user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting org: {str(e)}""")


@router.get("/{org_id}", response_model=dict)
def get_org(org_id: int):
    try:
        return organization.get_org(org_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting org: {str(e)}""")
