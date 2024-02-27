import os
from typing import List, Union
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

load_dotenv()

app = FastAPI()
llm = ChatOpenAI(temperature=1.0, model="gpt-3.5-turbo-0613", streaming=True)


class RequestData(BaseModel):
    message: str
    history: Union[List[List], List]


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = data["message"]
            history = data.get("history", [])

            # Process the message through the language model as done in the /predict endpoint
            history_langchain_format = []
            for human, ai in history:
                history_langchain_format.append(HumanMessage(content=human))
                history_langchain_format.append(AIMessage(content=ai))
            history_langchain_format.append(HumanMessage(content=message))
            gpt_response = llm(history_langchain_format).content

            # Send back the response to the client
            await manager.send_personal_message(gpt_response, websocket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)
