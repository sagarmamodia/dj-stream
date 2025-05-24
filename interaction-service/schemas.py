from pydantic import BaseModel
from datetime import datetime

class LikesResponse(BaseModel):
    video_id: str
    likes: int

class DislikesResponse(BaseModel):
    video_id: str
    dislikes: int

class CommentsResponse(BaseModel):
    user_id: str
    video_id: str
    content: str
    created_at: datetime 

class CommentRequest(BaseModel):
    # user_id: str
    video_id: str
    content: str
