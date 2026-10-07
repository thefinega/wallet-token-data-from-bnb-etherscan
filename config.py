"""Application configuration: supported networks, API settings, environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Etherscan API V2: a single API key works across every supported chain.
API_BASE_URL = "https://api.etherscan.io/v2/api"
API_TIMEOUT_SECONDS = 15
API_KEY_ENV_VAR = "ETHERSCAN_API_KEY"
DEFAULT_NETWORK = "bsc"
DEFAULT_OUTPUT_FILE = "Token list.txt"


@dataclass(frozen=True)
class Network:
    """A supported EVM network and its explorer metadata."""

    key: str
    name: str
    chain_id: int
    native_symbol: str
    explorer_url: str


NETWORKS: dict[str, Network] = {
    "bsc": Network("bsc", "BNB Smart Chain", 56, "BNB", "https://bscscan.com"),
    "ethereum": Network("ethereum", "Ethereum", 1, "ETH", "https://etherscan.io"),
}


def get_network(key: str) -> Network:
    """Return the :class:`Network` for *key*, raising ``ValueError`` if unknown."""
    try:
        return NETWORKS[key.strip().lower()]
    except KeyError as exc:
        available = ", ".join(sorted(NETWORKS))
        raise ValueError(f"Unknown network '{key}'. Available networks: {available}") from exc


def _load_dotenv(path: str = ".env") -> None:
    """Load simple ``KEY=VALUE`` pairs from *path* into the environment.

    Existing environment variables are never overwritten. Missing files are
    ignored silently so that a ``.env`` file is optional.
    """
    env_path = Path(path)
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_api_key(explicit: str | None = None) -> str:
    """Resolve the Etherscan API key from an argument, the environment or ``.env``."""
    if explicit and explicit.strip():
        return explicit.strip()
    _load_dotenv()
    key = os.getenv(API_KEY_ENV_VAR, "").strip()
    if not key:
        raise RuntimeError(
            f"No API key found. Set the {API_KEY_ENV_VAR} environment variable or add "
            "it to a .env file. Create a free key at https://etherscan.io/myapikey"
        )
    return key
