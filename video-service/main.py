from fastapi import FastAPI, status
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Annotated, Union
from utils import JsonResponse

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db_temp = client['db_temp']
db_videos = client['db_videos']

upload_session = db_temp['upload_session']
chunks = db_temp['chunks']


# Models
class UploadSession(BaseModel):
    id: str
    filename: str
    total_chunks: int
    chunk_size: int

class Chunk(BaseModel):
    id: str
    upload_id: str
    chunk_number: int
    data: bytes

class UploadSessionRequest(BaseModel):
    filename: str
    chunk_size: int
    total_chunks: int
     
@app.get('/home/')
def home():
    return JsonResponse(error='worked')

@app.post('/video/upload/initiate/')
def initiate_upload(payload: UploadSessionRequest):
    if(payload.chunk_size > 256):
        return JsonResponse(error='Chunk size should be <= 256 bytes', status=400)

    # create an upload_session document for this request 
    try:
        id = str(upload_session.insert_one(payload.dict()).inserted_id)
    except:
        return JsonResponse(error='Failure to create upload session', status=500)
    
    return JsonResponse(upload_session_id=id, status=200)
    
    
if __name__=='__main__':
    app.run(port=8000)

