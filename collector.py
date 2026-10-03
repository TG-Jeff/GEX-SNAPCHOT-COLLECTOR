import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


ASSETS = ["BTC", "ETH", "SOL", "XRP", "HYPE"]

DERIBIT_BASE = "https://www.deribit.com/api/v2/public"


def get_json(endpoint, params):
    url = f"{DERIBIT_BASE}/{endpoint}?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "crypto-gex-collector/1.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():

    captured_at = datetime.now(timezone.utc)

    print("=" * 70)
    print("CRYPTO GEX SNAPSHOT")
    print("=" * 70)
    print("UTC:", captured_at.isoformat())

    # ---------------------------------------------------------
    # 1. Get active USDC option instruments
    # ---------------------------------------------------------

    print("\nDownloading instrument metadata...")

    instruments_response = get_json(
        "get_instruments",
        {
            "currency": "USDC",
            "kind": "option",
            "expired": "false"
        }
    )

    instruments = instruments_response["result"]

    instrument_map = {
        x["instrument_name"]: x
        for x in instruments
    }

    print("Total active USDC options:", len(instruments))

    # ---------------------------------------------------------
    # 2. Get current option book summaries
    # ---------------------------------------------------------

    print("Downloading option summaries...")

    summary_response = get_json(
        "get_book_summary_by_currency",
        {
            "currency": "USDC",
            "kind": "option"
        }
    )

    summaries = summary_response["result"]

    print("Total option summaries:", len(summaries))

    # ---------------------------------------------------------
    # 3. Keep only our five assets
    # ---------------------------------------------------------

    prefixes = tuple(f"{asset}_USDC-" for asset in ASSETS)

    options = []

    for summary in summaries:

        instrument_name = summary.get("instrument_name", "")

        if not instrument_name.startswith(prefixes):
            continue

        metadata = instrument_map.get(instrument_name)

        if metadata is None:
            continue

        asset = instrument_name.split("_USDC-", 1)[0]

        option_type = metadata.get("option_type")

        row = {
            "asset": asset,
            "instrument_name": instrument_name,

            "strike": metadata.get("strike"),
            "option_type": option_type,

            "expiration_timestamp": metadata.get(
                "expiration_timestamp"
            ),

            "contract_size": metadata.get(
                "contract_size"
            ),

            "mark_price": summary.get(
                "mark_price"
            ),

            "mark_iv": summary.get(
                "mark_iv"
            ),

            "bid_price": summary.get(
                "bid_price"
            ),

            "ask_price": summary.get(
                "ask_price"
            ),

            "volume": summary.get(
                "volume"
            ),

            "open_interest": summary.get(
                "open_interest"
            ),

            "underlying_price": summary.get(
                "underlying_price"
            ),
        }

        options.append(row)

    # ---------------------------------------------------------
    # 4. Sort data
    # ---------------------------------------------------------

    options.sort(
        key=lambda x: (
            x["asset"],
            x["expiration_timestamp"] or 0,
            x["strike"] or 0,
            x["option_type"] or ""
        )
    )

    # ---------------------------------------------------------
    # 5. Statistics
    # ---------------------------------------------------------

    asset_counts = {}

    for asset in ASSETS:
        asset_counts[asset] = sum(
            1 for x in options
            if x["asset"] == asset
        )

    print("\nOptions collected:")

    for asset in ASSETS:
        print(
            f"  {asset}: {asset_counts[asset]}"
        )

    # ---------------------------------------------------------
    # 6. Create snapshot
    # ---------------------------------------------------------

    snapshot = {
        "captured_at_utc": captured_at.isoformat(),

        "captured_timestamp_ms": int(
            captured_at.timestamp() * 1000
        ),

        "source": "Deribit public API",

        "assets": ASSETS,

        "option_count": len(options),

        "asset_counts": asset_counts,

        "options": options
    }

    # ---------------------------------------------------------
    # 7. Save snapshot
    # ---------------------------------------------------------

    date_folder = captured_at.strftime("%Y-%m-%d")
    time_name = captured_at.strftime("%H%M%S")

    output_folder = (
        Path("data")
        / "raw"
        / date_folder
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_folder
        / f"snapshot_{time_name}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            snapshot,
            f,
            indent=2
        )

    print("\nSaved:")
    print(output_file)

    print("\nDONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
