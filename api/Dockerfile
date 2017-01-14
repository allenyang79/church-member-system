FROM python:2.7

MAINTAINER Allen Yang (a2279871@gmail.com)

RUN apt-get update
RUN apt-get install -y python-pip python-dev build-essential libffi-dev libssl-dev
RUN pip install -U pip

WORKDIR /srv/api
ENV PYTHONPATH=/srv/api
ADD requirement.txt requirement.txt

EXPOSE 5000
RUN pip install -r requirement.txt
