.ONESHELL:

build:
	echo Building rekdoc ...
	source venv/bin/activate
	pip install -r requirements.txt 
	pyinstaller --hidden-import wand \
		--hidden-import click \
		--hidden-import python-docx \
		-F rekdoc/core.py rekdoc/doc.py rekdoc/fetch.py rekdoc/const.py rekdoc/tools.py \
		-n rekdoc
	deactivate
	echo "#!/bin/sh ./rekdoc.py $@" > dist/rekdoc.sh

install:
	echo Building container
	docker build -t rekdoc -f Dockerfile .
run:
	# docker run -it --name rekdoc --rm rekdoc "$@"
	docker run -it -v $(pwd)/sample:/home/py/sample/  --name rekdoc --rm rekdoc "$@"
	
init:
	python -m venv venv

test: 
	./dist/rekdoc-1.0.0.pex -i input -o test
clean:
	rm -rf temp/*
	rm -rf output/*
	rm -f *.spec
purge: 
	rm -rf build dist
	rm -rf *.egg-info
tree:
	tree -I venv -I build -I dist -I __pycache__ -I *.egg-info
# .PHONY:
