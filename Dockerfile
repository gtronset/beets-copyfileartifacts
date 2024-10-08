FROM python:3.13-alpine

# Add dependencies for the reflink python module
RUN apk update && apk add python3-dev \
    cargo \
    gcc \
    gdal \
    libc-dev \
    libffi-dev

WORKDIR /src

COPY . /src
RUN pip install --upgrade pip \
    && pip install poetry pre-commit tox \
    && poetry install
