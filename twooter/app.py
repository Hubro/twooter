from contextlib import asynccontextmanager
from typing import Annotated

import fastapi
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import twooter.db
from twooter.message_stats import query_stats


@asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    await twooter.db.init()
    yield
    await twooter.db.teardown()


app = fastapi.FastAPI(lifespan=lifespan)

allow_origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return "Hello, world!"


class Message(BaseModel):
    text: str
    tag: str


@app.post("/messages")
async def post_message(input: Message):
    """Posts a new message to Twooter"""

    message = await twooter.db.Message.create(
        text=input.text,
        tag=input.tag,
    )

    return f"Posted new message: {message.id}"


@app.get("/messages")
async def get_messages(tag: str | None = None, limit: int | None = None):
    """Gets all messages, optionally filtered by tag"""

    messages = twooter.db.Message.all().order_by("-timestamp")

    if tag:
        messages = messages.filter(tag=tag)

    if limit:
        messages = messages.limit(limit)

    return await messages


@app.get("/management/message-stats")
async def get_management_messages_stats(
    start: Annotated[int, Query(ge=0, le=3000)] = 0,
    end: Annotated[int, Query(ge=0, le=3000)] = 3000,
) -> None:
    """Outputs message statistics grouped by year and tag

    Optionally provide a start and end time (both inclusive) to limit the
    timespan returned.
    """

    if end < start:
        return JSONResponse(
            status_code=400,
            content={"message": "end date must be greater than or equal to start date"},
        )

    return await query_stats(start, end)
