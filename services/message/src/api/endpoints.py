from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.core.organization import register_org


router = APIRouter()


@router.get("/organizations", response_model=List[dict])
def get_all_orgs():
    try:
        return []
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting all orgs: {str(e)}""")


@router.post("/organizations", response_model=int)
def create_org(org_name, creator_email):
    try:
        return register_org(org_name, creator_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering org: {str(e)}""")
