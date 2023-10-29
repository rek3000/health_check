init:
	python setup.py bdist_pex
test:
	./test.py -i input -o test
# gen:
	# python rek/rek.py
	# cat output/data.json
# doc:
# 	python rek/rekdoc.py
clean:
	rm -rf temp/*
	rm -rf output/*
.PHONY: init test
