"""Build request parameters for the Etherscan API V2."""

from __future__ import annotations

from config import API_BASE_URL


def build_api_url(
    api_key: str,
    chain_id: int,
    module: str,
    action: str,
    **extra: object,
) -> tuple[str, dict[str, object]]:
    """Return the ``(url, params)`` pair for an Etherscan API V2 request.

    ``None`` values in *extra* are dropped so callers can pass optional
    parameters unconditionally.
    """
    params: dict[str, object] = {
        "chainid": chain_id,
        "module": module,
        "action": action,
        "apikey": api_key,
    }
    params.update({key: value for key, value in extra.items() if value is not None})
    return API_BASE_URL, params
