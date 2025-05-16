from fastapi import FastAPI, status, Form, File, Depends, UploadFile
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Annotated, Union
from utils import JsonResponse
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db_temp = client['db_temp']
db_videos = client['db_videos']

upload_session = db_temp['upload_session']
chunks = db_temp['chunks']


# Models
class UploadSession(BaseModel):
    _id: str
    filename: str
    total_chunks: int
    chunk_size: int

class Chunk(BaseModel):
    _id: str #upload_id_{chunk_number}
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

@app.post('/video/upload/chunk/')
async def upload_chunk(
        upload_id: Annotated[str, Form(...)],
        filename: Annotated[str, Form(...)],
        chunk_number: Annotated[int, Form(...)],
        file: UploadFile = File(...)
):
    # retrieve session 
    try:
       session_id = upload_session.find({"_id": ObjectId(upload_id)})
    except:
        return JsonResponse(error="Failure to fetch upload session from database", status=500)
    
    if(session_id is None):
        return JsonResponse(error="Upload session does not exist", status=400)
    
    try:
        file_data = await file.read()
    except:
        return JsonResponse(error="Failure to read chunk data", status=500)

    # put chunk in the database
    try:
         chunk_obj = Chunk(
            _id=f"{upload_id}_{chunk_number}",
            upload_id=upload_id,
            chunk_number=chunk_number,
            data=file_data
        )
    except:
        return JsonResponse(error="Failure to generate a chunk object", status=500)

    try:  
        chunks.insert_one(chunk_obj.dict())
    except:
        return JsonResponse(error="Failure to put chunk in database", status=500)

    return JsonResponse(result='success')
    
if __name__=='__main__':
    app.run(port=8000)

