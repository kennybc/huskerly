import boto3
import uuid
from fastapi import FastAPI, HTTPException, File, UploadFile
from botocore.exceptions import ClientError
from typing import List


app = FastAPI(root_path="/upload")
bucket = boto3.resource("s3").Bucket("huskerly-attachments")
cdn = "https://d2o5rbazf3fhtp.cloudfront.net/"


@app.get("/")
def get_root():
    return {"name": "ms-upload", "data": "4"}


@app.post("/")
def post_attachment(files: List[UploadFile] = File(...)):
    distributions = []
    for file in files:
        key = str(uuid.uuid4().hex)
        try:
            content = file.file.read()
            if len(content) > 10485760:
                raise Exception("File size exceeds limit of 10 MB")
            bucket.put_object(
                Key=key,
                Body=content,
                ContentType=file.headers["content-type"],
            )
            distributions.append(cdn + key)
        except Exception as e:
            print(f"Failed to upload file ({file.filename}): {e}")
            return {"Status": "FAILED", "Error": e}

    return {"Status": "SUCCESS", "Distributions": distributions}
