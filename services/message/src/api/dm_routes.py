from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from typing import List
from core.chat import dm, shared as chat


router = APIRouter(prefix="/dm")

class DmGetRequest(BaseModel):
    current_user_email: str

@router.get("/{dm_id}/messages", response_model=dict)
def get_posts(dm_id: int, request: DmGetRequest):
    posts = chat.get_posts(request.current_user_email, dm_id)
    return {'Status': 'SUCCESS', 'Posts': posts}

    
@router.get("/{dm_id}", response_model=dict)
def get_dm(dm_id: int, request: DmGetRequest):
    dm_data = dm.get_dm(request.current_user_email, dm_id)
    return {'Status': 'SUCCESS', 'Data': dm_data}


class CreateDmRequest(BaseModel):
    current_user_email: str
    other_user_email: str
    org_id: int


@router.post("", response_model=dict)
def create_dm(request: CreateDmRequest):
    dm_id = dm.create_dm(request.current_user_email, request.other_user_email, request.org_id)
    return {'Status': 'SUCCESS', "dm_id": dm_id}
