FROM python:3.12

WORKDIR /app


RUN pip install uv


COPY . /app

RUN uv sync

EXPOSE 8000