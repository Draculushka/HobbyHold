from fastapi import FastAPI
from starlette.datastructures import MutableHeaders
from starlette.types import Message

def test_mutable_headers():
    message: Message = {
        "type": "http.response.start",
        "status": 200,
        "headers": []
    }
    try:
        # This is what's in main.py
        headers = MutableHeaders(scope=message)
        print("MutableHeaders(scope=message) worked")
    except Exception as e:
        print(f"MutableHeaders(scope=message) failed: {e}")

    try:
        headers = MutableHeaders(raw=message["headers"])
        print("MutableHeaders(raw=message['headers']) worked")
    except Exception as e:
        print(f"MutableHeaders(raw=message['headers']) failed: {e}")

if __name__ == "__main__":
    test_mutable_headers()
