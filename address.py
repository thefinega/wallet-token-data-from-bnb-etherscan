"""Read and validate an EVM wallet address from the user."""

from __future__ import annotations

import re

# An EVM address is 0x followed by exactly 40 hexadecimal characters.
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")


def is_valid_address(address: str) -> bool:
    """Return ``True`` when *address* looks like a syntactically valid EVM address."""
    return bool(ADDRESS_PATTERN.match(address.strip()))


def validate_address(address: str) -> str:
    """Return the trimmed *address* or raise ``ValueError`` if it is invalid."""
    candidate = address.strip()
    if not is_valid_address(candidate):
        raise ValueError(
            f"'{address}' is not a valid EVM address "
            "(expected 0x followed by 40 hex characters)."
        )
    return candidate


def get_address(prompt: str = "\nEnter address: ") -> str:
    """Prompt the user for a wallet address and validate it.

    Raises:
        ValueError: if the entered value is not a valid EVM address.
    """
    return validate_address(input(prompt))
