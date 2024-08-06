from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core import organization


router = APIRouter(prefix="/org")

class OrgGetAllRequest(BaseModel):
    current_user_email: str
    
@router.get("", response_model=dict, tags=['Public'])
def get_all_orgs(request: OrgGetAllRequest):
    orgs = organization.get_all_orgs(request.current_user_email)
    return {'Status': 'SUCCESS', 'Data': orgs}

class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("", response_model=dict, tags=['Private'])
def create_org(request: OrgCreateRequest):
    org_id = organization.create_org(request.org_name, request.creator_email)
    return {'Status': 'SUCCESS', "org_id": org_id}



class TransferOrgRequest(BaseModel):
    new_lead_admin_email: str
    current_user_email: str


@router.put("/{org_id}/transfer", response_model=dict, tags=['Public'])
def transfer_lead_admin(org_id: int, request: TransferOrgRequest):
    organization.transfer_lead_admin(
        org_id, request.new_lead_admin_email, request.current_user_email)
    return {'Status': 'SUCCESS'}

class PromoteToAssistAdminRequest(BaseModel):
    promoted_user_email: str
    current_user_email: str
    
@router.put("/{org_id}/promote", response_model=dict, tags=['Public'])
def promote_to_assist_admin(org_id: int, request: PromoteToAssistAdminRequest):
    organization.promote_to_assist_admin(
        org_id, request.promoted_user_email, request.current_user_email)
    return {'Status': 'SUCCESS'}

class DemoteRequest(BaseModel):
    demoted_user_email: str
    current_user_email: str

@router.put("/{org_id}/demote", response_model=dict, tags=['Public'])
def demote_to_member(org_id: int, request: DemoteRequest):
    organization.demote_to_member(
        org_id, request.demoted_user_email, request.current_user_email)
    return {'Status': 'SUCCESS'}


class OrgEditRequest(BaseModel):
    org_name: str
    current_user_email: str


@router.put("/{org_id}", response_model=dict, tags=['Public'])
def edit_org(org_id: int, request: OrgEditRequest):
    organization.edit_org(
        org_id, request.current_user_email, request.org_name)
    return {'Status': 'SUCCESS'}


class OrgDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{org_id}", response_model=dict, tags=['Public'])
def delete_org(org_id: int, request: OrgDeleteRequest):
    organization.delete_org(org_id, request.current_user_email)
    return {'Status': 'SUCCESS'}


@router.get("/{org_id}", response_model=dict, tags=['Public'])
def get_org(org_id: int):
    org_data = organization.get_org(org_id)
    return {'Status': 'SUCCESS', 'Data': org_data}
