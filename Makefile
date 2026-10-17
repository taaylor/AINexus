install-deps:
	uv sync --locked --group auth --group lint --group tests

generate-ci-jwt-keys:
	openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$$RUNNER_TEMP/jwt-private.pem"
	openssl pkey -in "$$RUNNER_TEMP/jwt-private.pem" -pubout -out "$$RUNNER_TEMP/jwt-public.pem"
	{ \
		echo 'JWT_PRIVATE_KEY<<JWT_PRIVATE_KEY_EOF'; \
		cat "$$RUNNER_TEMP/jwt-private.pem"; \
		echo 'JWT_PRIVATE_KEY_EOF'; \
		echo 'JWT_PUBLIC_KEY<<JWT_PUBLIC_KEY_EOF'; \
		cat "$$RUNNER_TEMP/jwt-public.pem"; \
		echo 'JWT_PUBLIC_KEY_EOF'; \
	} >> "$$GITHUB_ENV"

check-types:
	env -u PYTHONPATH uv run --no-sync pyrefly check

check-lint:
	uv run --no-sync ruff check services/auth

check-format:
	uv run --no-sync ruff format --check services/auth

ci-migrate:
	PYTHONPATH=services uv run --no-sync alembic -c services/auth/src/infrastructure/database/alembic.ini upgrade head

lint:
	PYTHONPATH=services uv run --group lint pyrefly check
	uv run --group lint ruff check --fix services/auth
	uv run --group lint ruff format services/auth

test:
	PYTHONPATH=services uv run --group auth --group tests pytest --rootdir=services/auth/tests services/auth/tests -q

pyclean:
	find services/auth -type f -name "*.pyc" -delete
	find services/auth -type d -name "__pycache__" -delete


auth-apprun:
	PYTHONPATH=services uv run --group auth uvicorn auth.src.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--log-level info \
		--log-config services/auth/src/common/json/logging.json \
		--access-log \
		--timeout-graceful-shutdown 10 \
		--lifespan on \
		--workers 1


migrate:
	PYTHONPATH=services uv run alembic -c services/auth/src/infrastructure/database/alembic.ini upgrade head

create-migrate: migrate
	PYTHONPATH=services uv run alembic -c services/auth/src/infrastructure/database/alembic.ini revision --autogenerate
