#!/bin/sh
#
# docker run -it -v $(pwd)/sample:/home/py/sample \
#     -v $(pwd)/output:/home/py/output \
#     -v $(pwd)/temp:/home/py/temp \
#     --name rekdoc --rm rekdoc "$@"
# docker run -it -v $(pwd)/sample:/home/py/sample \
#     -v $(pwd)/output:/home/py/output \
#     -v $(pwd)/temp:/home/py/temp \
#     --name rekdoc --rm rekdoc:1.0  
docker run -it -v $(pwd)/sample:/home/py/sample \
    -v $(pwd)/output:/home/py/output \
    -v $(pwd)/temp:/home/py/temp \
    --name rekdoc --rm health_check-rekdoc
