# Token data from BNB / Etherscan

Easily view a wallet's native balance and ERC-20 token holdings and save them to a file.

Data is read from the [Etherscan API V2](https://docs.etherscan.io/), which serves
both BNB Smart Chain and Ethereum through a single API key.

## Requirements

- Python 3.10+
- An Etherscan API key — create one free at <https://etherscan.io/myapikey>.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env      # then edit .env and set ETHERSCAN_API_KEY
```

The API key can also be exported as an environment variable instead of using `.env`:

```bash
export ETHERSCAN_API_KEY=your_api_key_here
```

## Usage

```bash
python main.py                                       # prompts for an address (BSC by default)
python main.py --address 0x... --network ethereum    # query Ethereum
python main.py -a 0x... -n bsc -o "Token list.txt"   # choose the output file
python main.py -a 0x... --no-write                   # print only, do not write a file
python main.py -a 0x... -v                           # verbose (debug) logging
```

### Example output

```
Network: BNB Smart Chain (chainid=56)
Address: 0x1234...abcd
Native balance: 1.234 BNB

Tokens (2):
  - USDT (Tether USD) [0x55d3...7955]: 12.5
  - CAKE (PancakeSwap Token) [0x0e09...e0a9]: 3.14
```

## Notes

- The `addresstokenbalance` endpoint (token holdings) requires an Etherscan
  **Standard (Pro)** plan. On the free tier, token holdings are skipped with a
  warning while the native balance is still shown.
- Results are appended to the output file (`Token list.txt` by default), one
  report per run.
- The tool is read-only: it never asks for and never needs a private key.

## Project layout

| File | Responsibility |
| --- | --- |
| `main.py` | CLI entry point and orchestration |
| `config.py` | Networks, API settings, environment/`.env` loading |
| `address.py` | Address prompt and validation |
| `url.py` | Builds Etherscan API V2 request parameters |
| `holdings.py` | Fetches and formats balances |
| `write.py` | Persists reports to disk |

## License

See [LICENSE](LICENSE).

