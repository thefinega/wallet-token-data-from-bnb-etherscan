"""CLI entry point: export the token holdings of an EVM wallet address."""

from __future__ import annotations

import argparse
import logging
import sys

from address import get_address, validate_address
from config import DEFAULT_NETWORK, DEFAULT_OUTPUT_FILE, NETWORKS, get_api_key, get_network
from holdings import get_holdings
from write import write_results

logger = logging.getLogger("wallet_token_data")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Print (and optionally save) the token holdings of a wallet address."
    )
    parser.add_argument("-a", "--address", help="Wallet address; prompted for if omitted.")
    parser.add_argument(
        "-n",
        "--network",
        default=DEFAULT_NETWORK,
        choices=sorted(NETWORKS),
        help="Network to query (default: %(default)s).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help="File to append results to (default: %(default)s).",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Only print the report; do not write it to a file.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the tool and return a process exit code."""
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        network = get_network(args.network)
        api_key = get_api_key()
        address = validate_address(args.address) if args.address else get_address()
    except (ValueError, RuntimeError) as exc:
        logger.error("%s", exc)
        return 1

    report = get_holdings(network, address, api_key)
    print("\n" + report.to_text() + "\n")

    if not args.no_write:
        try:
            path = write_results(args.output, report.to_text())
        except OSError as exc:
            logger.error("Could not write results to '%s': %s", args.output, exc)
            return 1
        logger.info("Results written to %s", path)

    return 0


if __name__ == "__main__":
    sys.exit(main())

