import os
from typing import Union, List

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from pydantic import BaseModel

load_dotenv()

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
    gpt_response = llm(history_langchain_format).content

    return {
        "content": gpt_response,
    }
