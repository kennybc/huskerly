import os
import boto3
import uuid
from fastapi import File, UploadFile, Form, FastAPI
from typing import List


app = FastAPI()

bucket = boto3.resource("s3").Bucket("huskerly-attachments")


@app.get("/")
def get_root():
    return {"name": "ms-upload", "data": "4"}


@app.post("/")
def post_attachment(files: List[UploadFile] = File(...)):
    keys = []
    for file in files:
        key = str(uuid.uuid4().hex)
        try:
            bucket.put_object(
                Key=key,
                Body=file.file.read(),
                ContentType=file.headers["content-type"],
            )
            keys.append(key)
        except Exception as e:
            print(f"Failed to upload file ({file.filename}): {e}")
            return {"Status": "FAILED"}

    return {"Status": "SUCCESS", "Keys": keys}
