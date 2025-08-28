up:
	docker compose up --build

down:
	docker compose down -v

fmt:
	black app tests
	isort app tests

lint:
	ruff app tests

test:
	pytest

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$$m"
