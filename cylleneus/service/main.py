import json
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED

from . import tasks


class CylleneusSource(BaseModel):
    corpus: str
    filename: str
    author: str = None
    title: str = None


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
    minscore: int = None
    top: int
    start_time: str
    end_time: str
    maxchars: int
    surround: int
    count: List[int]
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
        return json.loads(result.get())


@app.get("/corpus/", status_code=HTTP_200_OK)
async def corpus(c: str):
    result = tasks.corpus(c)
    return JSONResponse(content={c: result})


@app.post("/index/", status_code=HTTP_200_OK)
async def index(source: CylleneusSource):
    result = tasks.index(source.corpus, source.filename, source.author, source.title)
    return JSONResponse(content=result)
