import os
from pathlib import Path


def project_root() -> Path:
    """Return the repository root as a Path object."""
    return Path(__file__).resolve().parents[1]


def load_env(path: str | os.PathLike = ".env") -> None:
    """Load environment variables from a .env file if present (no dependency on dotenv here).

    This is a tiny helper. If you prefer python-dotenv, you can replace this with dotenv.load_dotenv.
    """
    p = Path(path)
    if not p.exists():
        return

    for line in p.read_text().splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
