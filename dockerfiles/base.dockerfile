FROM python:slim-buster as base
RUN apt update -y
RUN apt install python3-lxml libxslt-dev zlib1g-dev binutils libc-dev -y
RUN pip install --no-cache python-dotenv pyinstaller pillow python-docx mysql-connector-python click

RUN mkdir package
