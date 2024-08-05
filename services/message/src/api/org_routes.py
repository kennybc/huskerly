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
        org_id = organization.create_org(
            request.org_name, request.creator_email)
        return {'status': 'SUCCESS', "org_id": org_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering org: {str(e)}""")


class TransferOrgRequest(BaseModel):
    lead_admin_email: str
    current_user_email: str


@router.put("/{org_id}/transfer", response_model=dict)
def transfer_lead_admin(org_id: int, request: TransferOrgRequest):
    try:
        res = organization.transfer_lead_admin(
            org_id, request.lead_admin_email, request.current_user_email)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error transferring org: {str(e)}""")


class OrgEditRequest(BaseModel):
    org_name: str
    current_user_email: str


@router.put("/{org_id}", response_model=dict)
def edit_org(org_id: int, request: OrgEditRequest):
    try:
        res = organization.edit_org(
            org_id, request.current_user_email, request.org_name)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying org: {str(e)}""")


class OrgDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{org_id}", response_model=dict)
def delete_org(org_id: int, request: OrgDeleteRequest):
    try:
        res = organization.delete_org(org_id, request.current_user_email)
        return {'status': 'SUCCESS' if res else 'FAILED'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting org: {str(e)}""")


@router.get("/{org_id}", response_model=dict)
def get_org(org_id: int):
    try:
        org_data = organization.get_org(org_id)
        return {'status': 'SUCCESS', 'data': org_data}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting org: {str(e)}""")
