from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core import organization


router = APIRouter(prefix="/org")


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("", response_model=dict)
def create_org(request: OrgCreateRequest):
    org_id = organization.create_org(request.org_name, request.creator_email)
    return {'Status': 'SUCCESS', "org_id": org_id}



class TransferOrgRequest(BaseModel):
    lead_admin_email: str
    current_user_email: str


@router.put("/{org_id}/transfer", response_model=dict)
def transfer_lead_admin(org_id: int, request: TransferOrgRequest):
    organization.transfer_lead_admin(
        org_id, request.lead_admin_email, request.current_user_email)
    return {'Status': 'SUCCESS'}


class OrgEditRequest(BaseModel):
    org_name: str
    current_user_email: str


@router.put("/{org_id}", response_model=dict)
def edit_org(org_id: int, request: OrgEditRequest):
    organization.edit_org(
        org_id, request.current_user_email, request.org_name)
    return {'Status': 'SUCCESS'}


class OrgDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{org_id}", response_model=dict)
def delete_org(org_id: int, request: OrgDeleteRequest):
    organization.delete_org(org_id, request.current_user_email)
    return {'Status': 'SUCCESS'}


@router.get("/{org_id}", response_model=dict)
def get_org(org_id: int):
    org_data = organization.get_org(org_id)
    return {'Status': 'SUCCESS', 'Data': org_data}