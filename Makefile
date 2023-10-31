build:
	pyinstaller --hidden-import wand --hidden-import click -F rekdoc/* -n rekdoc
	# source venv/bin/activate; python setup.py bdist_pex
	
init:
	python -m venv venv
	source venv/bin/activate; pip install pex


test: 
	./dist/rekdoc-1.0.0.pex -i input -o test
clean:
	rm -rf temp/*
	rm -rf output/*
	rm -f *.spec
.PHONY: 
