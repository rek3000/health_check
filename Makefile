init:
	pip install -r requirements.txt
test:
	./tests/test.sh
run:
	python rek/rek.py
	cat output/data.json
.PHONY: init test
