.ONESHELL:

build:
	# echo Building rekdoc ...
	source venv/bin/activate
	mkdir -p target/local > /dev/null 2>&1
	pip install pyinstaller pillow mysql.connector click python-docx
	pyinstaller --strip --clean -F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py \
		-n rekdoc --distpath target/local
	deactivate

install:
	echo Building container
	docker build -t rek3000/rekdoc:1.0 -f dockerfiles/rekdoc.dockerfile .

build-gcc:
	mkdir -p target/docker > /dev/null 2>&1
	docker build -t rek3000/rekdoc:1.0-gcc -f dockerfiles/rekdoc-gcc.dockerfile .

install-gcc:
	docker run --rm -it \
		--mount type=bind,source="$(PWD)/target/",target="/home/py/target" \
		--name rekdoc-gcc rek3000/rekdoc:1.0-gcc /bin/bash -ci 'cp /usr/bin/rekdoc target/docker/'

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
# .PHONY:
