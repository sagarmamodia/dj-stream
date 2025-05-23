from fastapi import FastAPI, status, Form, File, Depends, UploadFile, Body, Request
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import Annotated, Union, Dict
from utils import JsonResponse
from bson.objectid import ObjectId
from gridfs import GridFS
import uuid
import pika

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db_temp = client['db_temp']
db_videos = client['db_videos']

upload_session = db_temp['upload_session']
chunks = db_temp['chunks']

fs = GridFS(db_videos)

# RabbitMQ configuration
# connection_parameters = pika.ConnectionParameters('localhost', port=5672)
# connection = pika.BlockingConnection(connection_parameters)
# channel = connection.channel()
# channel.queue_declare()

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
            
    # delete upload session and chunks put an event in the queue because this task can be done without making user wait for the response 
    return JsonResponse(file_id=str(file_id))

@app.get('/video/stream/{file_id}/')
def stream_video(request: Request, file_id: str):

    try:
        grid_out = fs.get(ObjectId(file_id)) 
    except:
        return JsonResponse(error="Failure to fetch video file from database", status=500)

    filesize = grid_out.length
    # read Range header 
    range_header = request.headers.get("Range")
    if range_header:
        try:
            unit, range_str = range_header.split("=")
            range_tuple = range_str.split("-")
            print(range_tuple)
            if len(range_tuple) == 1 or range_tuple[1]=='':
                start_str = range_tuple[0]
                end_str = str(filesize-1)
            elif len(range_tuple) == 2:
                start_str = range_tuple[0]
                end_str = range_tuple[1]

            start = int(start_str)
            end = int(end_str)

        except:
            return JsonResponse(error="Invalid range headers", status=400)
    else:
        start = 0
        end = filesize-1

    chunk_size = 1024*64

    def file_iterator(start_byte:int, end_byte:int):
        grid_out.seek(start_byte)
        bytes_left = end_byte-start_byte+1
        while bytes_left>0:
            read_len = min(chunk_size, bytes_left)
            data = grid_out.read(read_len)
            if not data:
                break 
            yield data 
            bytes_left -= len(data)

    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end-start+1),
        "Content-Range": f"bytes {start}-{end}/{filesize}",
      }

    return StreamingResponse(file_iterator(start, end), headers=headers, media_type="video/mp4", status_code=206)

@app.get('/home/')
def home():
    return JsonResponse(res="It works")
