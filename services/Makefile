lint:
	uv run --group lint pyrefly check
	uv run --group lint ruff check --fix
	uv run --group lint ruff format

pyclean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete


apprun:
	uv run --group auth uvicorn auth.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--log-level info \
		--log-config auth/common/json/logging.json \
		--access-log \
		--timeout-graceful-shutdown 10 \
		--lifespan on \
		--workers 2


migrate:
	uv run alembic -c auth/infrastructure/database/alembic.ini upgrade head

create-migrate: migrate
	uv run alembic -c auth/infrastructure/database/alembic.ini revision --autogenerate
