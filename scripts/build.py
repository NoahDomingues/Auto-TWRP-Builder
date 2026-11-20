#!/usr/bin/env python3

import argparse
import hashlib
from pathlib import Path

from twrpdtgen.device_tree import DeviceTree

STOCK_RECOVERY_SIZE = 33_554_432
STOCK_RECOVERY_SHA256 = "fea18b7c5c771054aec49559b09162be56dcc504667866fb2ffed54618886c07"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a starter device tree from the verified Alcatel 9032X stock recovery"
    )
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--expected-sha256", default=STOCK_RECOVERY_SHA256)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Stock recovery image not found: {args.input}")
    size = args.input.stat().st_size
    if size != STOCK_RECOVERY_SIZE:
        parser.error(f"Expected {STOCK_RECOVERY_SIZE} bytes, got {size}")
    actual = sha256_file(args.input)
    if actual.lower() != args.expected_sha256.strip().lower():
        parser.error(f"SHA-256 mismatch: {actual}")

    args.output.mkdir(parents=True, exist_ok=True)
    DeviceTree(args.input).dump_to_folder(args.output)
    boards = sorted(args.output.rglob("BoardConfig.mk"))
    if len(boards) != 1:
        raise RuntimeError(f"Expected exactly one BoardConfig.mk, found {len(boards)}")
    print(f"Stock recovery verified: {actual}")
    print(f"Generated starter tree: {boards[0].parent}")
    print("twrpdtgen generates a starter tree only; it does not compile or test a recovery.")


if __name__ == "__main__":
    main()
