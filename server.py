from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Hello from deployed Python backend!",
        "status": "success",
        "public": True,
        "try_me": [
            "Visit /random to get a random number",
            "Visit /echo?text=hello to echo text",
            "Visit /info to see server details"
        ]
    }

@app.get("/random")
def random_number():
    import random
    return {"random_number": random.randint(1, 100)}

@app.get("/echo")
def echo(text: str = "Hello World"):
    return {"echo": text, "received": True}

@app.get("/info")
def server_info():
    import datetime
    return {
        "server_time": str(datetime.datetime.now()),
        "python_version": "3.x",
        "framework": "FastAPI",
        "deployed": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)