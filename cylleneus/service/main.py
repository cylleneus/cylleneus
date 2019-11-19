import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from . import tasks


class CylleneusWork(BaseModel):
    corpus: str
    docix: int


class CylleneusQuery(BaseModel):
    query: str
    collection: List[CylleneusWork] = None


class CylleneusResult(BaseModel):
    corpus: str
    author: str
    title: str
    urn: str
    reference: str
    text: str


class CylleneusSearch(BaseModel):
    query: str
    collection: List[CylleneusWork]
    minscore: int
    top: int
    start_time: datetime
    end_time: datetime
    maxchars: int
    surround: int
    count: int
    results: List[CylleneusResult]


app = FastAPI()


@app.post("/search/", status_code=HTTP_202_ACCEPTED)
async def search(query: CylleneusQuery):
    result = tasks.search.delay(query.query, query.collection)
    return JSONResponse(content={"id": result.id})


@app.get("/status/")
async def status(id: str):
    result = tasks.search.AsyncResult(id)

    return {"status": result.status}


@app.get("/results/", status_code=HTTP_200_OK, response_model=CylleneusSearch)
async def results(id: str):
    result = tasks.search.AsyncResult(id)

    if result.ready():
        return result.get()
        # response = JSONResponse(content={"result": result.get()})


@app.get("/index/", status_code=HTTP_200_OK)
async def index(corpus: str):
    result = tasks.index(corpus)
    return JSONResponse(content={corpus: result})
