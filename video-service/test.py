import requests
import os
import math

file_path = 'test_file.jpg'
chunk_size = 1024*1024
file_size_bytes = os.path.getsize(file_path)
total_chunks = math.ceil(file_size_bytes / chunk_size)

# get upload id
print(file_size_bytes, chunk_size, total_chunks)
response = requests.post(
    'http://localhost:8000/video/upload/initiate/',
    json={'filename':'test_file.jpg', 'chunk_size': chunk_size, 'total_chunks': total_chunks}
)

print(response.json())
upload_id = response.json()['upload_session_id']

file = open(file_path, 'rb')
for i in range(total_chunks):
    chunk = file.read(chunk_size)
    files = {'file': ('test_file.jpg', chunk, 'application/octet-stream')}
    requests.post(
        'http://localhost:8000/video/upload/chunk/',
        files=files,
        data={'upload_id': upload_id, 'filename': 'test_file.jpg', 'chunk_number': i}
    )

response = requests.post(
    'http://localhost:8000/video/upload/complete/',
     json = {'upload_id': upload_id}
)

print(response.json())
