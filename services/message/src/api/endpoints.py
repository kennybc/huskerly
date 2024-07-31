from fastapi import APIRouter, HTTPException, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()


@router.get("/organizations", response_model=List[dict])
def get_all_orgs():
    try:
        return []
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting all orgs: {str(e)}""")
