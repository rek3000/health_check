# FROM debian:experimental
FROM python:alpine as base
# RUN apt update -y
# RUN apt -t experimental install --no-install-recommends libc6 -y
# RUN apt clean && rm -rf /var/lib/apt/lists/*
# RUN apt autoremove -y
# RUN rm -rf /usr/share/*
# RUN rm -rf /usr/locale/*
# RUN useradd py
RUN mkdir package
WORKDIR /package
RUN apk add --no-cache pkgconf binutils
RUN pip install --no-cache pyinstaller pillow python-docx mysql.connector click
COPY rekdoc /package/rekdoc/
RUN pyinstaller --strip --clean -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py -n rekdoc
# COPY requirements.txt .
# RUN rm -rf /home/py/build
USER py
CMD ["sh"]
FROM alpine:3.18.4 as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN adduser -D py
WORKDIR /home/py
USER py
# ENTRYPOINT ["./rekdoc"]
