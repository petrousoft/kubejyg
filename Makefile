build:
	python -m build
upload-test:
	python -m twine upload --repository testpypi dist/*
upload:
	python -m twine upload --repository pypi dist/*
