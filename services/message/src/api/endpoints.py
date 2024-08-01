from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.organization import register_org


router = APIRouter()


class OrgCreateRequest(BaseModel):
    org_name: str
    creator_email: str


@router.post("/orgs", response_model=int)
def create_org(request: OrgCreateRequest):
    try:
        return register_org(request.org_name, request.creator_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering org: {str(e)}""")
