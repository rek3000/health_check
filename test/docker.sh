#!/bin/sh
# image=rek3000/rekdoc:1.0-alpine
image=$1
docker run -it -v $(pwd)/sample:/home/py/sample \
    -v $(pwd)/output:/home/py/output \
    -v $(pwd)/temp:/home/py/temp \
    --name rekdoc --rm $1 

