from typing import List
from fastapi import APIRouter, HTTPException, HTTPException
from pydantic import BaseModel
from core.chat import stream, shared as chat


router = APIRouter(prefix="/stream")


@router.get("/{stream_id}/messages", response_model=List[dict])
def get_posts(stream_id: int):
    try:
        return chat.get_posts(stream_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting posts: {str(e)}""")


class JoinStreamRequest(BaseModel):
    user_email: str


@router.post("/{stream_id}/join", response_model=bool)
def join_stream(stream_id: int, request: JoinStreamRequest):
    try:
        return chat.join_chat(stream_id, request.user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error joining stream: {str(e)}""")


class StreamDeleteRequest(BaseModel):
    current_user_email: str


@router.post("/{stream_id}/delete", response_model=bool)
def delete_stream(stream_id: int, request: StreamDeleteRequest):
    try:
        return stream.delete_stream(request.current_user_email, stream_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error deleting stream: {str(e)}""")


@router.get("/{stream_id}", response_model=dict)
def get_stream(stream_id: int):
    try:
        return stream.get_stream(stream_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error getting stream: {str(e)}""")


class StreamCreateRequest(BaseModel):
    stream_name: str
    creator_email: str
    team_id: int


@router.post("", response_model=int)
def create_stream(request: StreamCreateRequest):
    try:
        return stream.create_stream(request.stream_name, request.creator_email, request.team_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error registering stream: {str(e)}""")


class StreamEditRequest(BaseModel):
    current_user_email: str
    stream_name: str
    public: bool


@router.put("/{stream_id}", response_model=bool)
def edit_stream(stream_id: int, request: StreamEditRequest):
    try:
        return stream.edit_stream(request.current_user_email, stream_id, request.stream_name, request.public)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error modifying stream: {str(e)}""")


class StreamLeaveRequest(BaseModel):
    current_user_email: str
    user_email: str


@router.delete("/{stream_id}", response_model=bool)
def leave_stream(stream_id: int, request: StreamLeaveRequest):
    try:
        return stream.leave_stream(stream_id, request.current_user_email, request.user_email)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"""Error leaving stream: {str(e)}""")
