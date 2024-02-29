import json
import os

from dotenv import load_dotenv
import gradio as gr
import websockets

load_dotenv()

END_TOKEN = os.environ.get("END_TOKEN", "1234ASDFzxcv")


class ConnectionHandler:
    def __init__(self, websocket_url: str) -> None:
        self.websocket_url = websocket_url
        self.websocket = None

    async def connect_to_websocket(self):
        if self.websocket is None or self.websocket.closed:
            self.websocket = await websockets.connect(self.websocket_url)

    async def send_and_receive_messages(self, message, history):
        # Prepare the data as per the original predict method's requirement
        await self.connect_to_websocket()
        data = {"message": message, "history": history}

        # convert the Python dict into JSON object.
        data_json = json.dumps(data)

        await self.websocket.send(data_json)
        # As 27/02/2024, gr.ChatInterface does not allow passing
        # via streaming the one chuck at a time. So we accumulate
        # chucks while receiving them.
        response = ""
        # Asynchronously iterating over the websocket responses.
        async for chunk in self.websocket:
            # If the token is not the end token `<generation_completed>`, then we are
            # continuing out stream into gradio UI.
            if chunk != END_TOKEN:
                response += chunk
                yield response
            else:
                break


if __name__ == "__main__":
    # initilise chatstorage object used to store previous messages.
    chat = ConnectionHandler(websocket_url="ws://localhost:8000/ws/chat")
    app = gr.ChatInterface(fn=chat.send_and_receive_messages)
    app.launch(share=True)
