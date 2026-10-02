lint:
	uv run --group lint pyrefly check
	uv run --group lint ruff check --fix
	uv run --group lint ruff format

pyclean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete


apprun:
	uv run gunicorn auth.main:app \
		--worker-class asgi \
		--logger-class auth.common.logger.GunicornLoguruLogger \
		--bind 0.0.0.0:8000 \
		--access-logfile - \
		--access-logformat '%(h)s %(m)s %(U)s %(s)s %(L)s s' \
		--graceful-timeout 10 \
		--asgi-lifespan on \
		--log-level info \
		--capture-output

migrate:
	uv run alembic -c auth/infrastructure/database/alembic.ini upgrade head

create-migrate: migrate
	uv run alembic -c auth/infrastructure/database/alembic.ini revision --autogenerate
