FROM python:3.10-slim

WORKDIR /app/src
COPY . .

RUN pip install -r requirements.txt

VOLUME ["/out"]

ENTRYPOINT [ "python", "./main.py"]
