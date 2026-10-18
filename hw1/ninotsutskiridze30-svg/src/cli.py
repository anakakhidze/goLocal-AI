"""Offline campus announcement CLI."""
import argparse
from datetime import date
import json

from extractor import process


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text")
    parser.add_argument("--today", type=date.fromisoformat, required=True)
    parser.add_argument("--rooms", nargs="+", default=["B204"], help="Canonical room codes")
    args = parser.parse_args()
    print(json.dumps(process(args.text, args.today, set(args.rooms))))


if __name__ == "__main__":
    main()
