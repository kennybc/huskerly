from fastapi import FastAPI

app = FastAPI(root_path="/user", debug=True)


@app.get("/")
def get_root():
    return {"name": "ms-user-test-3", "data": "3"}
