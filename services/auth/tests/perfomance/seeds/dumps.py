import os
import tempfile
from pathlib import Path

from auth.tests.perfomance.seeds.models import SeedsResult


def save_seeds_result(*, result: SeedsResult, output_path: Path) -> Path:
    """Write seed data atomically with owner-only permissions."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as output_file:
            temporary_path = Path(output_file.name)
            output_file.write(result.model_dump_json(indent=2))
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())

        temporary_path.chmod(0o600)
        temporary_path.replace(output_path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return output_path


def load_seeds_result(*, input_path: Path) -> SeedsResult:
    return SeedsResult.model_validate_json(input_path.read_text(encoding="utf-8"))
