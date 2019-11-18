import os
from typing import List, Tuple

from celery.result import AsyncResult
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from . import tasks


class Query(BaseModel):
    query: str
    collection: List[Tuple[str, int]] = None


# Adjust as appropriate
root_dir = os.path.expanduser('')
load_dotenv(os.path.join(root_dir, '.env'))

app = FastAPI()


@app.post("/query/")
async def query(query: Query):
    q = query["query"]
    c = query["collection"]
    result = tasks.search.delay(q, c)
    return JSONResponse(status_code=HTTP_202_ACCEPTED, content={
        'id': result.id,
    })


@app.get("/status/{id}")
async def status(id):
    result = AsyncResult(id=id, backend='redis://localhost')

    return {"status": result.status}


@app.get("/results/{id}")
async def results(id):
    result = AsyncResult(id=id, backend='redis://localhost')

    if result.ready():
        if result.result:
            response = JSONResponse(status_code=HTTP_200_OK, content={
                "result": result.result
            })
        else:
            response = JSONResponse(status_code=HTTP_204_NO_CONTENT)
    else:
        response = JSONResponse(status_code=HTTP_400_BAD_REQUEST)
    return response
