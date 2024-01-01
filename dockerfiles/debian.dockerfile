FROM python:slim-buster as base
RUN apt update -y
RUN apt install libc-dev -y
RUN apt install python3-lxml libxslt-dev zlib1g-dev -y
RUN apt install binutils -y
RUN pip install --no-cache python-dotenv pyinstaller pillow python-docx mysql-connector-python click
# RUN useradd py
RUN mkdir package
# RUN mkdir package
# USER py
WORKDIR /package/
COPY src/ /package/rekdoc/
RUN pyinstaller --strip --clean \
    -F rekdoc/rekdoc/core.py rekdoc/rekdoc/doc.py rekdoc/rekdoc/fetch.py rekdoc/rekdoc/const.py rekdoc/rekdoc/tools.py \
		--add-binary rekdoc/oswbba.jar:. \
    -n rekdoc

FROM debian:buster-slim as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN useradd py -u 1000
USER py
WORKDIR /home/py
