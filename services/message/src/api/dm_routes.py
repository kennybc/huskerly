from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from typing import List
from core.chat import dm, shared as chat


router = APIRouter(prefix="/dm")


@router.get("/{dm_id}/messages", response_model=List[dict])
def get_posts(dm_id: int):
    try:
        return chat.get_posts(dm_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting posts: {str(e)}""")


@router.get("/{dm_id}", response_model=dict)
def get_dm(dm_id: int):
    try:
        return dm.get_dm(dm_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting dm: {str(e)}""")


class CreateDmRequest(BaseModel):
    current_user_email: str
    other_user_email: str
    org_id: int


@router.post("", response_model=int)
def create_dm(request: CreateDmRequest):
    try:
        return dm.create_dm(request.current_user_email, request.other_user_email, request.org_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error creating dm: {str(e)}""")
