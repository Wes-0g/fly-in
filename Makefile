run:
	python3.10 fly-in.py $(map)

install:
	python3.10 -m pip install -r requirements.txt

debug:
	python3.10 -m pdb fly-in.py $(map)

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

.PHONY: run install debug clean lint
