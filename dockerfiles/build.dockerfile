FROM 127.0.0.1:3000/rek3000/rekdoc as base

RUN mkdir package
WORKDIR /package/
COPY rekdoc/ /package/rekdoc
RUN pyinstaller --clean \
    -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py \
    -n rd
