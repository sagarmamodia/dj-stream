import requests

response = requests.get('http://localhost:8000/video/stream/6830486b7d3eb5a5f5d50801/', stream=True)

for chunk in response.iter_content(chunk_size=65536):
    print("Chunk present")

