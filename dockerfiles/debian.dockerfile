FROM python:bookworm as base
RUN apt update -y
RUN apt install libc-bin=2.17 libc-bin=2.17 python3-lxml libxslt-dev zlib1g-dev -y
RUN pip install --no-cache pyinstaller pillow python-docx mysql-connector-python click
# RUN useradd py
RUN mkdir package
WORKDIR /package
# RUN mkdir package
# USER py
COPY rekdoc/ /package/rekdoc/
RUN pyinstaller --strip --clean \
    -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py -n rekdoc

FROM debian:bookworm-slim as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN useradd py -u 1000
USER py
WORKDIR /home/py
