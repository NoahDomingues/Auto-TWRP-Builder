#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

SUPER_PARTITION_SIZE = 4949278720
DYNAMIC_PARTITION_GROUP_SIZE = 4947181568
RECOVERY_PARTITION_SIZE = 33554432

DEVICE_CODENAME = "apollo2"
DEVICE_MANUFACTURER_DIR = "tcl"
DEVICE_PATH = "device/tcl/apollo2"
STOCK_FINGERPRINT = "Alcatel/9032X/Apollo_8_4G:10/QP1A.190711.020/1E24:user/release-keys"
STOCK_BUILD_DESC = "full_apollo2-user 10 QP1A.190711.020 1E24 release-keys"
DYNAMIC_PARTITIONS = "system vendor product odm oem"


def set_make_var(content: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*(?::=|\?=|\+=)\s*.*$", re.MULTILINE)
    replacement = f"{name} := {value}"
    if pattern.search(content):
        content = pattern.sub("", content, count=0)
        content = content.rstrip() + "\n" + replacement + "\n"
    else:
        content = content.rstrip() + "\n" + replacement + "\n"
    return content


def remove_make_vars(content: str, names: set[str]) -> str:
    for name in names:
        content = re.sub(
            rf"^\s*{re.escape(name)}\s*(?::=|\?=|\+=)\s*.*(?:\n|$)",
            "",
            content,
            flags=re.MULTILINE,
        )
    return content


def locate_board_config(root: Path) -> Path:
    candidates = list(root.rglob("BoardConfig.mk"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one BoardConfig.mk, found {len(candidates)}")
    board = candidates[0]
    if board.parent.name != DEVICE_CODENAME:
        raise RuntimeError(f"Unexpected device codename folder: {board.parent.name}")
    return board


def normalize_manufacturer_path(board: Path) -> Path:
    manufacturer_dir = board.parent.parent
    if manufacturer_dir.name == "alps":
        target = manufacturer_dir.parent / DEVICE_MANUFACTURER_DIR
        if target.exists():
            raise RuntimeError(f"Cannot rename alps to tcl because {target} already exists")
        manufacturer_dir.rename(target)
        return target / DEVICE_CODENAME / "BoardConfig.mk"
    if manufacturer_dir.name != DEVICE_MANUFACTURER_DIR:
        raise RuntimeError(f"Unexpected manufacturer directory: {manufacturer_dir.name}")
    return board


def replace_device_path_references(device_dir: Path) -> None:
    extensions = {".mk", ".bp", ".sh", ".rc", ".xml", ".txt", ".prop", ".json"}
    for path in device_dir.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text.replace("device/alps/apollo2", DEVICE_PATH)
        updated = updated.replace("device/alps/", "device/tcl/")
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def place_make_vars_before(content: str, anchor: str, values: dict[str, str]) -> str:
    content = remove_make_vars(content, set(values))
    position = content.find(anchor)
    if position < 0:
        raise RuntimeError(f"Could not find BoardConfig anchor: {anchor}")
    block = "\n".join(f"{name} := {value}" for name, value in values.items())
    return content[:position] + block + "\n\n" + content[position:]


def patch_board_config(board_path: Path) -> None:
    text = board_path.read_text(encoding="utf-8")
    text = remove_make_vars(
        text,
        {
            "TARGET_2ND_ARCH",
            "TARGET_2ND_ARCH_VARIANT",
            "TARGET_2ND_CPU_ABI",
            "TARGET_2ND_CPU_ABI2",
            "TARGET_2ND_CPU_VARIANT",
            "TARGET_2ND_CPU_VARIANT_RUNTIME",
            "TARGET_KERNEL_SOURCE",
            "TARGET_KERNEL_CONFIG",
            "BOARD_BOOTIMAGE_PARTITION_SIZE",
            "BOARD_ALPS_DYNAMIC_PARTITIONS_SIZE",
            "BOARD_ALPS_DYNAMIC_PARTITIONS_PARTITION_LIST",
        },
    )

    values = {
        "DEVICE_PATH": DEVICE_PATH,
        "TARGET_BOARD_PLATFORM": "mt6761",
        "TARGET_BOOTLOADER_BOARD_NAME": "MT6761",
        "TARGET_ARCH": "arm",
        "TARGET_ARCH_VARIANT": "armv7-a-neon",
        "TARGET_CPU_ABI": "armeabi-v7a",
        "TARGET_CPU_ABI2": "armeabi",
        "TARGET_CPU_VARIANT": "cortex-a53",
        "TARGET_CPU_VARIANT_RUNTIME": "cortex-a53",
        "TARGET_USES_64_BIT_BINDER": "false",
        "TARGET_FORCE_PREBUILT_KERNEL": "true",
        "TARGET_PREBUILT_KERNEL": "$(DEVICE_PATH)/prebuilt/kernel",
        "TARGET_PREBUILT_DTB": "$(DEVICE_PATH)/prebuilt/dtb.img",
        "BOARD_KERNEL_IMAGE_NAME": "zImage",
        "BOARD_BOOTIMG_HEADER_VERSION": "2",
        "BOARD_KERNEL_PAGESIZE": "2048",
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE": str(RECOVERY_PARTITION_SIZE),
        "BOARD_SUPER_PARTITION_SIZE": str(SUPER_PARTITION_SIZE),
        "VENDOR_SECURITY_PATCH": "2099-12-31",
        "TW_INCLUDE_CRYPTO": "true",
        "TW_INCLUDE_CRYPTO_FBE": "true",
        "TW_INCLUDE_FBE": "true",
        "TW_INCLUDE_FBE_METADATA_DECRYPT": "true",
        "BOARD_USES_METADATA_PARTITION": "true",
        "BOARD_SUPER_PARTITION_GROUPS": "main",
        "BOARD_MAIN_SIZE": str(DYNAMIC_PARTITION_GROUP_SIZE),
        "BOARD_MAIN_PARTITION_LIST": DYNAMIC_PARTITIONS,
        "BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE": "f2fs",
        "TARGET_USERIMAGES_USE_EXT4": "true",
        "TARGET_USERIMAGES_USE_F2FS": "true",
        "TARGET_RECOVERY_FSTAB": "$(DEVICE_PATH)/recovery.fstab",
    }
    for name, value in values.items():
        text = set_make_var(text, name, value)

    prebuilt_vars = {
        "DEVICE_PATH": DEVICE_PATH,
        "TARGET_FORCE_PREBUILT_KERNEL": "true",
        "TARGET_PREBUILT_KERNEL": "$(DEVICE_PATH)/prebuilt/kernel",
        "TARGET_PREBUILT_DTB": "$(DEVICE_PATH)/prebuilt/dtb.img",
    }
    text = place_make_vars_before(
        text,
        "ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)",
        prebuilt_vars,
    )

    dtb_arg = "BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)"
    if dtb_arg not in text:
        text = text.rstrip() + "\n" + dtb_arg + "\n"

    board_path.write_text(text, encoding="utf-8")


def patch_device_makefile(device_dir: Path) -> None:
    path = device_dir / "device.mk"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    text = remove_make_vars(text, {"PRODUCT_USE_DYNAMIC_PARTITIONS", "PRODUCT_SHIPPING_API_LEVEL"})
    text = set_make_var(text, "LOCAL_PATH", "$(call my-dir)")
    text = set_make_var(text, "PRODUCT_USE_DYNAMIC_PARTITIONS", "true")
    text = set_make_var(text, "PRODUCT_SHIPPING_API_LEVEL", "29")
    path.write_text(text, encoding="utf-8")


def patch_product_makefile(device_dir: Path) -> Path:
    candidates = sorted(device_dir.glob("omni_*.mk"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one omni_*.mk product file, found {len(candidates)}")
    path = candidates[0]
    text = path.read_text(encoding="utf-8")
    values = {
        "PRODUCT_DEVICE": DEVICE_CODENAME,
        "PRODUCT_NAME": "omni_apollo2",
        "PRODUCT_BRAND": "Alcatel",
        "PRODUCT_MODEL": "9032X",
        "PRODUCT_MANUFACTURER": "TCL",
        "PRIVATE_BUILD_DESC": f'"{STOCK_BUILD_DESC}"',
        "BUILD_FINGERPRINT": STOCK_FINGERPRINT,
    }
    for name, value in values.items():
        text = set_make_var(text, name, value)
    path.write_text(text, encoding="utf-8")
    return path


def patch_metadata_fstab(device_dir: Path) -> None:
    path = device_dir / "recovery.fstab"
    if not path.is_file():
        raise RuntimeError("recovery.fstab was not generated")

    lines = path.read_text(encoding="utf-8").splitlines()
    metadata_rows = [
        index
        for index, line in enumerate(lines)
        if line.strip() and not line.lstrip().startswith("#") and re.search(r"(^|\s)/metadata(\s|$)", line)
    ]
    if len(metadata_rows) != 1:
        raise RuntimeError(f"Expected one /metadata fstab row, found {len(metadata_rows)}")

    index = metadata_rows[0]
    line = lines[index]
    if "/dev/block/mmcblk0p16" not in line:
        if not re.search(r"/dev/block/\S+", line):
            raise RuntimeError("Could not identify the /metadata block device in recovery.fstab")
        lines[index] = re.sub(r"/dev/block/\S+", "/dev/block/mmcblk0p16", line, count=1)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_recovery_init(device_dir: Path) -> None:
    path = device_dir / "recovery/root/init.recovery.mt6761.rc"
    if not path.is_file():
        raise RuntimeError("recovery/root/init.recovery.mt6761.rc was not generated")

    text = path.read_text(encoding="utf-8")
    import_line = re.compile(r"^\s*import\s+/init\.recovery\.smartlog\.rc\s*$", re.MULTILINE)
    smartlog_files = list(device_dir.rglob("init.recovery.smartlog.rc"))
    if import_line.search(text) and not smartlog_files:
        text = import_line.sub(
            "# Optional stock smartlog init file was not present in the extracted recovery ramdisk.",
            text,
        )
        path.write_text(text, encoding="utf-8")


def validate_prebuilt_files(device_dir: Path) -> None:
    expected = {
        "kernel": 8637050,
        "dtb.img": 78570,
        "dtbo.img": 60296,
    }
    for name, expected_size in expected.items():
        path = device_dir / "prebuilt" / name
        if not path.is_file():
            raise RuntimeError(f"Missing prebuilt file: {path}")
        actual_size = path.stat().st_size
        if actual_size != expected_size:
            raise RuntimeError(f"Unexpected size for {name}: {actual_size}, expected {expected_size}")


def write_report(device_dir: Path) -> None:
    report = [
        "Alcatel 9032X / Apollo_8_4G device-tree correction report",
        "",
        f"Device tree path: {DEVICE_PATH}",
        "Platform: MT6761; Android stock base: 10 / API 29",
        "Userspace architecture: ARM32 (armeabi-v7a)",
        f"Super partition size: {SUPER_PARTITION_SIZE} bytes",
        f"Dynamic group main maximum size: {DYNAMIC_PARTITION_GROUP_SIZE} bytes (verified by lpdump)",
        f"Dynamic partitions: {DYNAMIC_PARTITIONS}",
        "Recovery partition size: 33554432 bytes",
        "Metadata block device: /dev/block/mmcblk0p16",
        "Stock fingerprint: " + STOCK_FINGERPRINT,
        "",
        "TWRP FBE crypto support is enabled; successful decryption still depends on the device-specific fstab and MediaTek keymaster components.",
        "The TWRP build compatibility values PLATFORM_VERSION=16.1.0 and security patch 2099-12-31 are preserved.",
        "No recovery image was built or flashed by this script.",
    ]
    (device_dir / "DEVICE_TREE_FIX_REPORT.txt").write_text("\n".join(report) + "\n", encoding="utf-8")


def fix_tree(root: Path) -> Path:
    if not root.is_dir():
        raise RuntimeError(f"Device tree root does not exist: {root}")
    board = locate_board_config(root)
    board = normalize_manufacturer_path(board)
    device_dir = board.parent

    replace_device_path_references(device_dir)
    patch_board_config(board)
    patch_device_makefile(device_dir)
    product_file = patch_product_makefile(device_dir)
    patch_metadata_fstab(device_dir)
    patch_recovery_init(device_dir)
    validate_prebuilt_files(device_dir)
    write_report(device_dir)

    final_text = board.read_text(encoding="utf-8")
    required = {
        "DEVICE_PATH": DEVICE_PATH,
        "TARGET_BOARD_PLATFORM": "mt6761",
        "TARGET_ARCH": "arm",
        "TARGET_ARCH_VARIANT": "armv7-a-neon",
        "TARGET_CPU_ABI": "armeabi-v7a",
        "TARGET_CPU_ABI2": "armeabi",
        "TARGET_CPU_VARIANT": "cortex-a53",
        "TARGET_CPU_VARIANT_RUNTIME": "cortex-a53",
        "TARGET_USES_64_BIT_BINDER": "false",
        "TARGET_FORCE_PREBUILT_KERNEL": "true",
        "TARGET_PREBUILT_KERNEL": "$(DEVICE_PATH)/prebuilt/kernel",
        "TARGET_PREBUILT_DTB": "$(DEVICE_PATH)/prebuilt/dtb.img",
        "BOARD_KERNEL_IMAGE_NAME": "zImage",
        "BOARD_BOOTIMG_HEADER_VERSION": "2",
        "BOARD_KERNEL_PAGESIZE": "2048",
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE": str(RECOVERY_PARTITION_SIZE),
        "BOARD_SUPER_PARTITION_SIZE": str(SUPER_PARTITION_SIZE),
        "VENDOR_SECURITY_PATCH": "2099-12-31",
        "TW_INCLUDE_CRYPTO": "true",
        "TW_INCLUDE_CRYPTO_FBE": "true",
        "TW_INCLUDE_FBE": "true",
        "TW_INCLUDE_FBE_METADATA_DECRYPT": "true",
        "BOARD_USES_METADATA_PARTITION": "true",
        "BOARD_SUPER_PARTITION_GROUPS": "main",
        "BOARD_MAIN_SIZE": str(DYNAMIC_PARTITION_GROUP_SIZE),
        "BOARD_MAIN_PARTITION_LIST": DYNAMIC_PARTITIONS,
        "TARGET_RECOVERY_FSTAB": "$(DEVICE_PATH)/recovery.fstab",
    }
    for name, value in required.items():
        if not re.search(rf"^\s*{name}\s*:=\s*{re.escape(value)}\s*$", final_text, re.MULTILINE):
            raise RuntimeError(f"Validation failed: {name} != {value}")

    force_pos = final_text.find("TARGET_FORCE_PREBUILT_KERNEL := true")
    conditional_pos = final_text.find("ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)")
    if force_pos < 0 or conditional_pos < 0 or force_pos > conditional_pos:
        raise RuntimeError("TARGET_FORCE_PREBUILT_KERNEL must be set before its conditional block")

    if "BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img" not in final_text:
        raise RuntimeError("Prebuilt DTBO image path is missing or was not enabled")

    if "BOARD_BOOTIMAGE_PARTITION_SIZE" in final_text:
        raise RuntimeError("Unverified boot partition size must not be hardcoded")

    product_text = product_file.read_text(encoding="utf-8")
    product_required = {
        "PRODUCT_DEVICE": DEVICE_CODENAME,
        "PRODUCT_NAME": "omni_apollo2",
        "PRODUCT_BRAND": "Alcatel",
        "PRODUCT_MODEL": "9032X",
        "PRODUCT_MANUFACTURER": "TCL",
        "BUILD_FINGERPRINT": STOCK_FINGERPRINT,
    }
    for name, value in product_required.items():
        if not re.search(rf"^\s*{name}\s*:=\s*{re.escape(value)}\s*$", product_text, re.MULTILINE):
            raise RuntimeError(f"Product identity validation failed: {name} != {value}")

    device_text = (device_dir / "device.mk").read_text(encoding="utf-8")
    if not re.search(r"^\s*PRODUCT_USE_DYNAMIC_PARTITIONS\s*:=\s*true\s*$", device_text, re.MULTILINE):
        raise RuntimeError("PRODUCT_USE_DYNAMIC_PARTITIONS is not enabled in device.mk")

    fstab_text = (device_dir / "recovery.fstab").read_text(encoding="utf-8")
    metadata_rows = [
        line for line in fstab_text.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and re.search(r"(^|\s)/metadata(\s|$)", line)
    ]
    if len(metadata_rows) != 1 or "/dev/block/mmcblk0p16" not in metadata_rows[0]:
        raise RuntimeError("Metadata fstab validation failed")

    init_text = (device_dir / "recovery/root/init.recovery.mt6761.rc").read_text(encoding="utf-8")
    if "import /init.recovery.smartlog.rc" in init_text and not list(device_dir.rglob("init.recovery.smartlog.rc")):
        raise RuntimeError("Recovery init still imports a missing smartlog file")

    if re.search(r"^\s*(TARGET_KERNEL_SOURCE|TARGET_KERNEL_CONFIG|TARGET_2ND_ARCH)\s*(?::=|\?=|\+=)", final_text, re.MULTILINE):
        raise RuntimeError("Unexpected kernel-source or 64-bit secondary-architecture setting remains")

    print(f"Fixed device tree: {device_dir}")
    print(f"BoardConfig: {board}")
    print(f"Product file: {product_file}")
    print("Validation: passed")
    return device_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct and validate the Alcatel 9032X TWRP device tree")
    parser.add_argument("--root", type=Path, required=True, help="Directory containing the generated manufacturer/codename tree")
    args = parser.parse_args()
    fix_tree(args.root)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"Device tree correction failed: {error}")
