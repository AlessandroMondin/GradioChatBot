import os
from typing import Union, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from pydantic import BaseModel

load_dotenv()

END_TOKEN = os.environ.get("END_TOKEN", "1234ASDFzxcv")

app = FastAPI()
llm = ChatOpenAI(temperature=1.0, model="gpt-3.5-turbo-0613")


class RequestData(BaseModel):
    message: str
    history: Union[List[List], List]


@app.post("/predict")
async def reply(file: RequestData):
    history_langchain_format = []
    for human, ai in file.history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=file.message))

    # https://python.langchain.com/docs/expression_language/streaming
    async def stream_response():
        async for chunk in llm.astream(history_langchain_format):
            yield chunk.content
        yield END_TOKEN

    # set media_type="text/event-stream" because of https://stackoverflow.com/a/75760884
    return StreamingResponse(stream_response(), media_type="text/event-stream")
