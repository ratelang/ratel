FROM python:latest

WORKDIR /usr/src/ratl

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --editable .[dev]
