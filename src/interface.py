import os

from dotenv import load_dotenv
import gradio as gr
import requests

load_dotenv()

END_TOKEN = os.environ.get("END_TOKEN", "1234ASDFzxcv")


def predict(message, history):
    # Assuming your FastAPI endpoint is set up to receive a POST request at /predict
    url = "http://localhost:8000/predict/"
    data = {"message": message, "history": history}

    response = ""
    s = requests.Session()
    with s.post(url, headers=None, json=data, stream=True) as r:
        # https://requests.readthedocs.io/en/latest/api/
        # "A value of None will function differently depending on the value of
        # stream. stream=True will read data as it arrives in whatever size the
        #  chunks are received"
        for chunk in r.iter_content(chunk_size=None):
            chunk = chunk.decode("utf-8")
            if chunk != END_TOKEN:
                response += chunk
                yield response
            else:
                break


if __name__ == "__main__":
    gr.ChatInterface(
        fn=predict,
    ).launch()
