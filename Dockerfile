FROM python:3.13-rc-alpine
RUN adduser py
WORKDIR /home/py
COPY ./dist/rekdoc /usr/bin/
USER py
COPY script/rekdoc.sh .
RUN chmod +x rekdoc.sh
CMD ["bash"]
ENTRYPOINT ["./rekdoc.sh"]

