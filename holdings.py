"""Fetch native and ERC-20 token balances for a wallet via the Etherscan API."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

import requests

from config import API_TIMEOUT_SECONDS, Network
from url import build_api_url

logger = logging.getLogger(__name__)

NATIVE_DECIMALS = 18


@dataclass(frozen=True)
class TokenHolding:
    """A single ERC-20 token balance held by a wallet."""

    symbol: str
    name: str
    address: str
    quantity: Decimal
    price_usd: Decimal | None = None


@dataclass
class WalletReport:
    """The full set of balances for one wallet on one network."""

    network: Network
    address: str
    native_balance: Decimal | None = None
    tokens: list[TokenHolding] = field(default_factory=list)

    def to_text(self) -> str:
        """Render the report as a human-readable block of text."""
        lines = [
            f"Network: {self.network.name} (chainid={self.network.chain_id})",
            f"Address: {self.address}",
        ]
        if self.native_balance is not None:
            lines.append(
                f"Native balance: {self.native_balance} {self.network.native_symbol}"
            )
        lines.append("")
        if self.tokens:
            lines.append(f"Tokens ({len(self.tokens)}):")
            lines.extend(
                f"  - {token.symbol} ({token.name}) [{token.address}]: {token.quantity}"
                for token in self.tokens
            )
        else:
            lines.append("Tokens: none found")
        return "\n".join(lines)


def _request_json(url: str, params: dict[str, object]) -> dict:
    """Perform a GET request and return the decoded JSON body."""
    safe_params = {**params, "apikey": "***"}
    logger.debug("GET %s params=%s", url, safe_params)
    try:
        response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"Request to the explorer API timed out after {API_TIMEOUT_SECONDS} seconds."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error while contacting the explorer API: {exc}") from exc
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("The explorer API returned a non-JSON response.") from exc


def _api_error(data: dict) -> str:
    """Extract a readable error message from an Etherscan API response."""
    result = data.get("result")
    if isinstance(result, str) and result:
        return result
    return str(data.get("message", "unknown error"))


def _to_decimal(raw_value: object, divisor: int, *, context: str) -> Decimal | None:
    """Convert a raw integer string into a scaled :class:`Decimal`."""
    try:
        return Decimal(str(raw_value)) / (Decimal(10) ** divisor)
    except (InvalidOperation, ValueError):
        logger.warning("Could not parse %s value: %r", context, raw_value)
        return None


def fetch_native_balance(network: Network, address: str, api_key: str) -> Decimal:
    """Return the native coin balance (in whole coins) for *address*."""
    url, params = build_api_url(
        api_key, network.chain_id, "account", "balance", address=address, tag="latest"
    )
    data = _request_json(url, params)
    if data.get("status") != "1":
        raise RuntimeError(f"Explorer API error: {_api_error(data)}")
    balance = _to_decimal(data.get("result"), NATIVE_DECIMALS, context="native balance")
    if balance is None:
        raise RuntimeError("Explorer API returned an invalid native balance.")
    return balance


def fetch_token_holdings(network: Network, address: str, api_key: str) -> list[TokenHolding]:
    """Return the ERC-20 tokens held by *address*.

    Uses the ``addresstokenbalance`` endpoint, which requires an Etherscan
    Standard (Pro) plan. On the free tier the API reports an error and an empty
    list is returned so the rest of the report is still produced.
    """
    url, params = build_api_url(
        api_key, network.chain_id, "account", "addresstokenbalance", address=address
    )
    data = _request_json(url, params)
    if data.get("status") != "1":
        logger.warning("Token holdings unavailable: %s", _api_error(data))
        return []
    result = data.get("result")
    if not isinstance(result, list):
        logger.warning("Unexpected token holdings payload; skipping tokens.")
        return []

    holdings: list[TokenHolding] = []
    for item in result:
        divisor = int(item.get("TokenDivisor") or NATIVE_DECIMALS)
        quantity = _to_decimal(item.get("TokenQuantity"), divisor, context="token balance")
        if quantity is None:
            continue
        price = _to_decimal(item.get("TokenPriceUSD"), 0, context="token price")
        holdings.append(
            TokenHolding(
                symbol=str(item.get("TokenSymbol", "?")),
                name=str(item.get("TokenName", "?")),
                address=str(item.get("TokenAddress", "?")),
                quantity=quantity,
                price_usd=price,
            )
        )
    return holdings


def get_holdings(network: Network, address: str, api_key: str) -> WalletReport:
    """Fetch native and token balances, logging (not raising) per-endpoint errors."""
    report = WalletReport(network=network, address=address)
    try:
        report.native_balance = fetch_native_balance(network, address, api_key)
    except RuntimeError as exc:
        logger.error("Could not fetch native balance: %s", exc)
    try:
        report.tokens = fetch_token_holdings(network, address, api_key)
    except RuntimeError as exc:
        logger.error("Could not fetch token holdings: %s", exc)
    return report
