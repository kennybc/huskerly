FROM python:3.8

# 
WORKDIR /app

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./src /app

# 
CMD ["fastapi", "run", "server.py", "--port", "80"]