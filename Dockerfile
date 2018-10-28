FROM python:3.6.7

MAINTAINER Ivan Tk <fatgrout@yahoo.com>

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN mkdir /code
COPY . /code/
WORKDIR /code/cnn
RUN pip install -r requirements.txt
