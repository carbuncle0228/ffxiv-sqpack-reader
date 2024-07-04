build:
	poetry install
	poetry export --without-hashes --with dev --with test --output requirements.txt

test:
	TZ=UTC pytest -s

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .
