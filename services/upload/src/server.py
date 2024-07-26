from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root():
    return {"name": "ms-upload", "data": "3"}
