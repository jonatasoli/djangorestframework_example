FROM python:3.7-alpine
MAINTAINER Jonatas Oliveira

ENV PYTHONUNBUFFERED 1

COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install pipenv && \
    pipenv install --system

RUN apk del .tmp-build-deps

RUN mkdir /src
WORKDIR /src
COPY . /src

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user

RUN chown -R user:user /vol/
RUN chmod -R 775 /vol/web
RUN chown -R user:user /src/
RUN chmod -R 775 /src

USER user
