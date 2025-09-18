from fastapi import FastAPI, Query
from es_client import es, INDEX_NAME
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"], # Allows all methods
#     allow_headers=["*"],
# )

@app.get('/search/health')
def health_check():
    return {"status": "OK"}

@app.get("/search")
def search_videos(q: str = Query(..., description="Search query")):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["title", "description", "channel_name"]
                }
            }
        },
    )

    results = [
        {
            "id": hit["_id"],
            "score": hit["_score"],
            "title": hit["_source"]["title"],
            "description": hit["_source"]["description"],
            "channel_name": hit["_source"]["channel_name"],
        }
        for hit in response["hits"]["hits"]
    ]
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)