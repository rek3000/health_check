FROM python:bookworm as base
RUN mkdir package
WORKDIR /package
# RUN apk add --no-cache pkgconf binutils
RUN apt update -y
RUN apt install gcc python3-lxml libxslt-dev zlib1g-dev -y
RUN pip install --no-cache pyinstaller pillow python-docx mysql-connector-python click
COPY rekdoc/ /package/rekdoc/
RUN pyinstaller --strip --clean \
    -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py -n rekdoc
USER py
CMD ["sh"]
FROM debian:bookworm-slim as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN useradd py
WORKDIR /home/py
USER py
