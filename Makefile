test:
	TZ=UTC pytest -s

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .
