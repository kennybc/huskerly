from fastapi import APIRouter
from pydantic import BaseModel
from core.chat import stream


router = APIRouter(prefix="/stream")

class StreamGetRequest(BaseModel):
    current_user_email: str

@router.get("/{stream_id}/messages", response_model=dict, tags=['Public'])
def get_posts(stream_id: int, request: StreamGetRequest):
    posts = stream.get_stream_posts(request.current_user_email, stream_id) #TODO:
    return {'Status': 'SUCCESS', 'Posts': posts}

@router.get("/{stream_id}", response_model=dict, tags=['Public'])
def get_stream(stream_id: int, request: StreamGetRequest):
    stream_data = stream.get_stream(request.current_user_email, stream_id)
    return {'Status': 'SUCCESS', 'Data': stream_data}

class JoinStreamRequest(BaseModel):
    user_email: str


@router.post("/{stream_id}/join", response_model=dict, tags=['Public'])
def join_stream(stream_id: int, request: JoinStreamRequest):
    stream.join_stream(stream_id, request.user_email)
    return {'Status': 'SUCCESS'}

class StreamLeaveRequest(BaseModel):
    current_user_email: str
    user_email: str


@router.post("/{stream_id}/leave", response_model=dict, tags=['Public'])
def leave_stream(stream_id: int, request: StreamLeaveRequest):
    stream.leave_stream(stream_id, request.current_user_email, request.user_email)
    return {'Status': 'SUCCESS'}


class StreamDeleteRequest(BaseModel):
    current_user_email: str


@router.delete("/{stream_id}", response_model=dict, tags=['Public'])
def delete_stream(stream_id: int, request: StreamDeleteRequest):
    stream.delete_stream(request.current_user_email, stream_id)
    return {'Status': 'SUCCESS'}

class StreamCreateRequest(BaseModel):
    stream_name: str
    public: bool
    creator_email: str
    team_id: int


@router.post("", response_model=dict, tags=['Public'])
def create_stream(request: StreamCreateRequest):
    stream_id = stream.create_stream(request.stream_name, request.public, request.creator_email, request.team_id)
    return {'Status': 'SUCCESS', "stream_id": stream_id}


class StreamEditRequest(BaseModel):
    current_user_email: str
    stream_name: str
    public: bool


@router.put("/{stream_id}", response_model=dict, tags=['Public'])
def edit_stream(stream_id: int, request: StreamEditRequest):
    stream.edit_stream(request.current_user_email, stream_id, request.stream_name, request.public)
    return {'Status': 'SUCCESS'}



