import ast
import gradio as gr
import requests


def predict(message, history):
    # Assuming your FastAPI endpoint is set up to receive a POST request at /predict
    url = "http://localhost:8000/predict/"
    data = {"message": message, "history": history}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        content = ast.literal_eval(response.content.decode("utf-8"))["content"]
        return content
    else:
        return "Error: Could not get a response from the FastAPI backend."


if __name__ == "__main__":
    gr.ChatInterface(
        fn=predict,
    ).launch()
