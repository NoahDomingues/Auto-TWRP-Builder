import argparse
from pathlib import Path

from twrpdtgen.device_tree import DeviceTree


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a TWRP device tree from a stock recovery image")
    parser.add_argument("-i", "--input", type=Path, required=True, help="Verified stock recovery image")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input image does not exist: {args.input}")

    args.output.mkdir(parents=True, exist_ok=True)
    device_tree = DeviceTree(args.input)
    device_tree.dump_to_folder(args.output)

    makefiles = sorted(args.output.rglob("Android.bp"))
    if len(makefiles) != 1:
        raise RuntimeError(f"Expected exactly one generated Android.bp, found {len(makefiles)}")
    print(makefiles[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
