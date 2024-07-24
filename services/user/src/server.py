from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root():
    return {"name": "ms-user", "data": "1"}
