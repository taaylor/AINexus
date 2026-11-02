import asyncio
import logging

from auth.tests.perfomance.api.auth_client import get_auth_api_client
from auth.tests.perfomance.seeds.builder import SeedsBuilder
from auth.tests.perfomance.seeds.dumps import save_seeds_result
from auth.tests.perfomance.seeds.models import SeedsPlan
from auth.tests.perfomance.settings import settings

logger = logging.getLogger(__name__)


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    plan = SeedsPlan(users_count=settings.seed_users_count)

    async with get_auth_api_client(settings.auth_api_http_client) as client:
        result = await SeedsBuilder(client).build(plan=plan)

    output_path = save_seeds_result(
        result=result,
        output_path=settings.seeds_output_path,
    )
    logger.info(
        "Created %d auth users. Seed data saved to %s.",
        len(result.users),
        output_path,
    )


if __name__ == "__main__":
    asyncio.run(run())
