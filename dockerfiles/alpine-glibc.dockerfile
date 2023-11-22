FROM jeanblanchard/alpine-glibc:3.18 as base
RUN mkdir package
WORKDIR /package
RUN apk add --no-cache pkgconf binutils python3 py3-pip
RUN pip install --no-cache pyinstaller pillow python-docx mysql-connector-python click
COPY rekdoc/ /package/rekdoc/
RUN pyinstaller --strip --clean \
    -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py -n rekdoc

FROM jeanblanchard/alpine-glibc:3.18 as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN adduser -D py
WORKDIR /home/py
USER py
