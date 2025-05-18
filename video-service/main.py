from fastapi import FastAPI, status, Form, File, Depends, UploadFile, Body
from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import Annotated, Union, Dict
from utils import JsonResponse
from bson import ObjectId
from gridfs import GridFS
import uuid

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db_temp = client['db_temp']
db_videos = client['db_videos']

upload_session = db_temp['upload_session']
chunks = db_temp['chunks']

fs = GridFS(db_videos)

# Models
class UploadSession(BaseModel):
    _id: str
    filename: str
    total_chunks: int
    chunk_size: int

class Chunk(BaseModel):
    _id: str
    upload_id: str
    chunk_number: int
    data: bytes

class UploadSessionRequest(BaseModel):
    filename: str
    chunk_size: int
    total_chunks: int
   

@app.post('/video/upload/initiate/')
def initiate_upload(payload: UploadSessionRequest):
    if(payload.chunk_size > 1024*1024*16):
        return JsonResponse(error='Chunk size should be <= 16MB', status=400)

    # create an upload_session document for this request 
    upload_session_obj = UploadSession( filename=payload.filename, chunk_size=payload.chunk_size, total_chunks=payload.total_chunks)
    try:
        id = str(upload_session.insert_one(upload_session_obj.dict()).inserted_id)
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
       session = upload_session.find_one({"_id": ObjectId(upload_id)})
    except:
        return JsonResponse(error="Failure to fetch upload session from database", status=500)
    
    if(session is None):
        return JsonResponse(error="Upload session does not exist", status=400)

    try:
        file_data = await file.read()
    except:
        return JsonResponse(error="Failure to read chunk data", status=500)

    # put chunk in the database
    try:
         chunk_obj = Chunk(
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

@app.post('/video/upload/complete/')
def complete_upload(payload: Dict[str, str]):
    upload_id = payload['upload_id'] 
    try:
        upload_session_dict = upload_session.find_one({"_id": ObjectId(upload_id)})
    except: 
        return JsonResponse(error="Failure to retrieve upload session from database", status=500)  
    
    upload_session_obj = UploadSession(**upload_session_dict)

    #retrieve all the chunks 
    binary_chunks = []
    filename = upload_session_obj.filename
    total_chunks = upload_session_obj.total_chunks

    for i in range(total_chunks):
        try:
            chunk = chunks.find_one({"upload_id": upload_id, "chunk_number": i})
        except:
            # delete all the chunks and upload session
            return JsonResponse(error=f"Failure to fetch chunk {i} from database", status=500)
        
        binary_chunks.append(chunk['data']) 

    with open(filename, 'wb') as f:
        for chunk in binary_chunks:
            f.write(chunk)

        # save this file to mongodb
    
    with open(filename, 'rb') as f:
        f.seek(0)
        try:
            file_id = fs.put(f.read(), filename=filename)
        except:
            return JsonResponse(error="Failure to put merged file in database", status=500)
            
    with open('console.txt', 'w') as f:
        f.write(str(file_id))
   
    
    return JsonResponse(file_id=str(file_id))


if __name__=='__main__':
    app.run(port=8000)

