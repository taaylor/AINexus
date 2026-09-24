lint:
	uv run --group lint pyrefly check
	uv run --group lint ruff check --fix
	uv run --group lint ruff format

pyclean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete


apprun:
	uv run --group auth gunicorn auth.main:app \
		--worker-class asgi \
		--bind 0.0.0.0:8000 \
		--graceful-timeout 30 \
		--asgi-lifespan on