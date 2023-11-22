.ONESHELL:

build:
	# echo Building rekdoc ...
	source venv/bin/activate
	mkdir -p target/local > /dev/null 2>&1
	pip install pyinstaller pillow mysql.connector click python-docx
	pyinstaller --strip --clean -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py \
		-n rekdoc --distpath target/local
	deactivate

# install:
# 	echo Building container
# 	docker build -t rek3000/rekdoc:1.0 -f dockerfiles/rekdoc.dockerfile .

build-debian:
	mkdir -p target/docker/debian > /dev/null 2>&1
	docker build -t rek3000/rekdoc:1.0-deb -f dockerfiles/debian.dockerfile .
	docker run --rm -it \
		--mount type=bind,source="$(PWD)/target/",target="/home/py/target" \
		--name rekdoc-gcc rek3000/rekdoc:1.0-deb /bin/bash -ci 'cp /usr/bin/rekdoc target/docker/debian/'

build-alpine-glibc:
	mkdir -p target/docker/alpine-glibc > /dev/null 2>&1
	docker build -t rek3000/rekdoc:1.0-alpine-glibc -f dockerfiles/alpine-glibc.dockerfile .
	docker run --rm -it \
		--mount type=bind,source="$(PWD)/target/",target="/home/py/target" \
		--name rekdoc-gcc rek3000/rekdoc:1.0-alpine-glibc /bin/bash -ci 'cp /usr/bin/rekdoc target/docker/alpine-glibc/'

build-ol:
	mkdir -p target/docker/ol > /dev/null 2>&1
	docker build -t rek3000/rekdoc:1.0-ol -f dockerfiles/ol.dockerfile .
	docker run --rm -it \
		--mount type=bind,source="$(PWD)/target/",target="/home/py/target" \
		--name rekdoc-gcc rek3000/rekdoc:1.0-ol /bin/bash -ci 'cp /usr/bin/rekdoc target/docker/ol/'
# install-debian:

run:
	docker run -it -v $(pwd)/sample:/home/py/sample/ --name rekdoc --rm rekdoc "$@"
	
init:
	python -m venv venv

test: 
	./dist/rekdoc-1.0.0.pex -i input -o test
clean:
	rm -rf temp/*
	rm -rf output/*
	rm -f *.spec
purge: 
	rm -rf build dist target
	rm -rf *.egg-info
tree:
	tree -I venv -I build -I dist -I __pycache__ -I *.egg-info
.PHONY: build-debian
