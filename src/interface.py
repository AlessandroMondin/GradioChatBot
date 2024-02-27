import websockets
import json

import gradio as gr


class ChatInterface:
    def __init__(self) -> None:
        self.history = []
        self.websocket_url = "ws://localhost:8000/ws/chat"
        self.websocket = None

    async def connect_to_websocket(self):
        if self.websocket is None or self.websocket.closed:
            self.websocket = await websockets.connect(self.websocket_url)

    async def send_and_receive_messages(self, message, history):
        # Prepare the data as per the original predict method's requirement
        await self.connect_to_websocket()
        data = {"message": message, "history": history}

        # Convert the Python dictionary to a JSON formatted string
        data_json = json.dumps(data)

        # Send the message
        await self.websocket.send(data_json)

        # Wait for the server's response
        response = await self.websocket.recv()

        self.history.append([message, response])
        return response


if __name__ == "__main__":
    chat = ChatInterface()
    app = gr.ChatInterface(fn=chat.send_and_receive_messages)
    app.queue()
    app.launch()
