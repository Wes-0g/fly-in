run:
	python3.10 map_parser.py config.txt

install:
	python3.10 -m pip install -r requirements.txt

debug:
	python3.10 -m pdb

clean:
	rm -rf __pycache__ */__pycache__
	rm -rf .mypy_cache */.mypy_cache

lint:
	python3.10 -m flake8 .
	python3.10 -m mypy . --warn-return-any \
	 					 --warn-unused-ignores \
	 					 --ignore-missing-imports \
	 					 --disallow-untyped-defs \
	 					 --check-untyped-defs

lint-strict:
	python3.10 -m mypy . --strict


.PHONY: run install debug clean lint lint-strict
