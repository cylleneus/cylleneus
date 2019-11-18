import os
from typing import List

from celery.result import AsyncResult
#from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from . import tasks


class CylleneusWork(BaseModel):
    corpus: str
    docix: int


class CylleneusQuery(BaseModel):
    query: str
    collection: List[CylleneusWork] = None


# Adjust as appropriate
root_dir = os.path.expanduser('')
#load_dotenv(os.path.join(root_dir, '.env'))

app = FastAPI()


@app.post("/search/", status_code=HTTP_202_ACCEPTED)
async def search(query: CylleneusQuery):
    result = tasks.search.delay(query.query, query.collection)
    return JSONResponse(content={
        'id': result.id,
    })


@app.get("/status/")
async def status(id: str):
    result = tasks.search.AsyncResult(id)

    return {"status": result.status}


@app.get("/results/", status_code=HTTP_200_OK)
async def results(id: str):
    result = tasks.search.AsyncResult(id)

    if result.ready():
        response = JSONResponse(content={
                "result": result.get()
            })
    else:
        response = JSONResponse(status_code=HTTP_400_BAD_REQUEST)
    return response

@app.get("/index/", status_code=HTTP_200_OK)
async def index(corpus: str):
    result = tasks.index(corpus)    
    return JSONResponse(content={ corpus: result })
