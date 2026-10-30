# Performance API tooling

The package contains a typed async `httpx2` client for seed creation and a typed
Locust API client backed by Locust's synchronous HTTP session. Both import request
and response schemas from `auth`; there are no duplicate auth schemas.

Install the performance dependencies and run the seed builder from the
repository root:

```bash
uv sync --group perfomance
PYTHONPATH=services uv run --group perfomance python -m auth.tests.perfomance.seeds.cli
```

Configuration is read from environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `AUTH_API_HTTP_CLIENT.URL` | `http://localhost` | Base URL of the service or gateway |
| `AUTH_API_HTTP_CLIENT.TIMEOUT` | `10.0` | HTTP request timeout for seed and Locust clients |
| `SEED_USERS_COUNT` | `10` | Number of users to register |
| `SEEDS_OUTPUT_PATH` | `services/auth/tests/perfomance/dumps/auth-users.json` | Seed result file |

The JSON result contains generated usernames and passwords for later scenarios.
The default output directory is Git-ignored, and the file is created with
owner-only permissions. Keep any custom output path out of source control too.

Seed scripts await `get_auth_api_client` methods. Locust scenarios use
`get_auth_locust_api_client(client, config)` with the `HttpUser` client's
synchronous session. Locust records request duration, response size, route, and HTTP errors;
scenario task functions are synchronous.

To use the result later, call `load_seeds_result(input_path=Path(...))` from
`auth.tests.perfomance.seeds.dumps`. Each entry has `registration_input` and
`registration_output` fields.
