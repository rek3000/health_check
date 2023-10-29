init:
	python -m venv venv
	source venv/bin/activate; pip install pex
build:
	source venv/bin/activate; python setup.py bdist_pex

test: 
	./dist/rekdoc-1.0.0.pex -i input -o test
clean:
	rm -rf temp/*
	rm -rf output/*
.PHONY:  
