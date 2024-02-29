import os
from typing import List

from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

load_dotenv()

END_TOKEN = os.environ.get("END_TOKEN", "1234ASDFzxcv")

app = FastAPI()
llm = ChatOpenAI(temperature=1.0, model="gpt-3.5-turbo-0613", streaming=True)


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

            history_langchain_format = []
            for human, ai in history:
                history_langchain_format.append(HumanMessage(content=human))
                history_langchain_format.append(AIMessage(content=ai))
            history_langchain_format.append(HumanMessage(content=message))
            # asyncio streaming:
            # https://python.langchain.com/docs/expression_language/streaming
            async for chunk in llm.astream(history_langchain_format):
                await manager.send_personal_message(chunk.content, websocket)
            await manager.send_personal_message(END_TOKEN, websocket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.disconnect(websocket)
