init:
	pip install -r requirements.txt
test:
	./test.sh
run:
	python rek.py
	cat output/data.json
.PHONY: init test
