import requests
import os

file = open('test_file.jpg', 'rb')
chunk = file.read(256)

files = {'file': ('test_file.jpg', chunk, 'application/octet-stream')}

response = requests.post(
    'http://localhost:8000/video/upload/chunk/',
    files=files,
    data={'upload_id': '682782242188c34f0369feae', 'filename': 'test_file.jpg', 'chunk_number': 1}
)

print(response.json())
