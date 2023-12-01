FROM oraclelinux:7-slim as base
ENV PYI_STATIC_ZLIB=1
RUN yum update -y
RUN yum install gcc -y
RUN yum install python3 python3-pip python3-lxml libxslt-dev zlib1g-dev freetype-devel \
    python3-devel zlib-devel libjpeg-devel libraqm-devel -y
RUN pip3 install --no-cache wheel 
RUN pip3 install --no-cache pyinstaller python-docx mysql-connector click
# RUN yum install libtiff-devel openjpeg2-devel  \
#     lcms2-devel libwebp-devel tcl-devel tk-devel \
    # harfbuzz-devel fribidi-devel libimagequant-devel -y
# RUN pip3 install pillow 
RUN pip3 install pillow
RUN yum install dejavu-fonts-common -y
# RUN useradd py
RUN mkdir package
WORKDIR /package
# RUN mkdir package
# USER py
COPY rekdoc/ /package/rekdoc/
RUN pyinstaller -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py -n rekdoc

FROM oraclelinux:7-slim as final
COPY --from=base /package/dist/rekdoc /usr/bin/rekdoc 
RUN useradd py -u 1000
USER py
WORKDIR /home/py
