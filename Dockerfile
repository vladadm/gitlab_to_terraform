FROM python:3.9.13-alpine

WORKDIR /app
COPY src/* ./

RUN pip install -r requirements.txt

CMD ['ls', '-la']