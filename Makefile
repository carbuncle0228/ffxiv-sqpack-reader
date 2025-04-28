build:
	poetry install
	poetry export --without-hashes --with dev --with test --output requirements.txt
	python -m nuitka --standalone --onefile --output-dir=dist-linux/ --enable-plugin=pyside6 --include-package=app --windows-console-mode=disable main_ui.py

test:
	TZ=UTC pytest -s

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .

bench:
	pytest app/tests/bench.py
