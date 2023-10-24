init:
	pip install -r requirements.txt
test:
	./tests/test.sh
gen:
	python rek/rek.py
	cat output/data.json
doc:
	python rek/rekdoc.py
.PHONY: init test
