import requests
import os
import math

video_service = "localhost:8002"

file_path = 'codesoft task 4.webm'
filename = 'codesoft task 4.webm'
chunk_size = 1024*1024
file_size_bytes = os.path.getsize(file_path)
total_chunks = math.ceil(file_size_bytes / chunk_size)

# get upload id
# print(file_size_bytes, chunk_size, total_chunks)
response = requests.post(
    f'http://{video_service}/video/upload/initiate/',
    json={'filename':'test_video.mp4', 'chunk_size': chunk_size, 'total_chunks': total_chunks}
)

print(response.json())
upload_id = response.json()['upload_session_id']

file = open(file_path, 'rb')
print('Uploading process initiated...')
print(f'Total chunks - {total_chunks}')
print(f'Chunk size - {chunk_size}')
for i in range(total_chunks):
    print(f'Sending chunk {i}', end=" ")
    chunk = file.read(chunk_size)
    files = {'file': (filename, chunk, 'application/octet-stream')}
    requests.post(
        f'http://{video_service}/video/upload/chunk/',
        files=files,
        data={'upload_id': upload_id, 'filename': filename, 'chunk_number': i}
    )
    print("\tFinished")

response = requests.post(
    f'http://{video_service}/video/upload/complete/',
    json = {'upload_id': upload_id}
)

print(response.json())
