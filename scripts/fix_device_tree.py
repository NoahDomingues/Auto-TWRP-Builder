#!/usr/bin/env python3

import argparse
import re
import shutil
from pathlib import Path

SUPER_PARTITION_SIZE = 4_949_278_720
DYNAMIC_GROUP_SIZE = 4_947_181_568
RECOVERY_PARTITION_SIZE = 33_554_432
DEVICE = "apollo2"
DEVICE_PATH = "device/tcl/apollo2"
STOCK_FINGERPRINT = "Alcatel/9032X/Apollo_8_4G:10/QP1A.190711.020/1E24:user/release-keys"
STOCK_BUILD_DESC = "full_apollo2-user 10 QP1A.190711.020 1E24 release-keys"
SECURITY_PATCH = "2021-11-05"
DYNAMIC_PARTITIONS = "system vendor product odm oem"
EXPECTED_FILES = {
    "kernel": 8_637_050,
    "dtb/mt6761.dtb": 78_570,
    "recovery_dtbo.img": 60_296,
}
INVALID_PARTITIONS = ("md1dsp", "md1arm7", "md3img", "odmdtbo")


def assignment_pattern(name):
    return re.compile(r"^[ \t]*" + re.escape(name) + r"[ \t]*(?::=|\?=|\+=)[^\n]*", re.MULTILINE)


def set_make_var(content, name, value):
    replacement = f"{name} := {value}"
    pattern = assignment_pattern(name)
    if pattern.search(content):
        content = pattern.sub(replacement, content)
    else:
        content = content.rstrip() + "\n" + replacement
    return content.rstrip() + "\n"


def remove_make_vars(content, names):
    for name in names:
        content = assignment_pattern(name).sub("", content)
    return content


def find_board(root):
    found = list(root.rglob("BoardConfig.mk"))
    if len(found) != 1:
        raise RuntimeError(f"Expected one BoardConfig.mk, found {len(found)}")
    board = found[0]
    if board.parent.name != DEVICE:
        raise RuntimeError(f"Unexpected device folder: {board.parent.name}")
    return board


def normalize_device_path(board):
    manufacturer = board.parent.parent
    if manufacturer.name == "alps":
        target = manufacturer.parent / "tcl"
        if target.exists():
            raise RuntimeError(f"Cannot rename alps: {target} already exists")
        manufacturer.rename(target)
        return target / DEVICE / "BoardConfig.mk"
    if manufacturer.name != "tcl":
        raise RuntimeError(f"Unexpected manufacturer folder: {manufacturer.name}")
    return board


def replace_device_paths(device_dir):
    extensions = {".mk", ".bp", ".sh", ".rc", ".xml", ".txt", ".prop", ".json"}
    for path in device_dir.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        try:
            old = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = old.replace("device/alps/apollo2", DEVICE_PATH).replace("device/alps/", "device/tcl/")
        if new != old:
            path.write_text(new, encoding="utf-8")


def normalize_prebuilt(device_dir):
    prebuilt = device_dir / "prebuilt"
    if not (prebuilt / "kernel").is_file():
        raise RuntimeError("Missing stock prebuilt kernel")

    dtb_old = prebuilt / "dtb.img"
    dtb_dir = prebuilt / "dtb"
    dtb_dir.mkdir(parents=True, exist_ok=True)
    dtb_new = dtb_dir / "mt6761.dtb"
    if dtb_old.is_file() and not dtb_new.exists():
        shutil.move(str(dtb_old), str(dtb_new))

    dtbo_old = prebuilt / "dtbo.img"
    dtbo_new = prebuilt / "recovery_dtbo.img"
    if dtbo_old.is_file() and not dtbo_new.exists():
        shutil.move(str(dtbo_old), str(dtbo_new))

    for relative, expected in EXPECTED_FILES.items():
        path = prebuilt / relative
        if not path.is_file() or path.stat().st_size != expected:
            actual = path.stat().st_size if path.is_file() else "missing"
            raise RuntimeError(f"Prebuilt {relative}: got {actual}, expected {expected} bytes")


def insert_before(content, anchor, block):
    content = remove_make_vars(content, set(block))
    position = content.find(anchor)
    rendered = "\n".join(f"{key} := {value}" for key, value in block.items())
    if position < 0:
        return content.rstrip() + "\n\n" + rendered + "\n"
    return content[:position].rstrip() + "\n\n" + rendered + "\n\n" + content[position:]


def patch_mkbootimg_args(content):
    lines = []
    for line in content.splitlines():
        if re.match(r"^[ \t]*BOARD_MKBOOTIMG_ARGS[ \t]*(?::=|\?=|\+=)", line):
            line = re.sub(r"\s+--dtb\s+\$\(TARGET_PREBUILT_DTB\)", "", line)
            line = re.sub(r"\s+--dtb\s+\$\(DEVICE_PATH\)/prebuilt/dtb\.img", "", line)
            line = re.sub(r"\s+--header_version\s+\S+", "", line)
        lines.append(line)
    content = "\n".join(lines).rstrip()
    return content + "\nBOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOTIMG_HEADER_VERSION)\n"


def patch_board(board):
    content = board.read_text(encoding="utf-8")
    content = remove_make_vars(content, {
        "TARGET_2ND_ARCH", "TARGET_2ND_ARCH_VARIANT", "TARGET_2ND_CPU_ABI",
        "TARGET_2ND_CPU_ABI2", "TARGET_2ND_CPU_VARIANT",
        "TARGET_2ND_CPU_VARIANT_RUNTIME", "TARGET_KERNEL_SOURCE",
        "TARGET_KERNEL_CONFIG", "TARGET_PREBUILT_DTB",
        "BOARD_BOOTIMAGE_PARTITION_SIZE", "BOARD_ALPS_DYNAMIC_PARTITIONS_SIZE",
        "BOARD_ALPS_DYNAMIC_PARTITIONS_PARTITION_LIST", "BOARD_KERNEL_SEPARATED_DTBO",
        "BOARD_AVB_ENABLE", "BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS",
        "BOARD_AVB_RECOVERY_KEY_PATH", "BOARD_AVB_RECOVERY_ALGORITHM",
        "BOARD_AVB_RECOVERY_ROLLBACK_INDEX", "BOARD_AVB_RECOVERY_ROLLBACK_INDEX_LOCATION",
        "TW_INCLUDE_CRYPTO", "TW_INCLUDE_CRYPTO_FBE", "TW_INCLUDE_FBE",
        "TW_INCLUDE_FBE_METADATA_DECRYPT", "PLATFORM_VERSION", "PLATFORM_VERSION_LAST_STABLE",
    })

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
        "BOARD_KERNEL_IMAGE_NAME": "zImage",
        "BOARD_BOOTIMG_HEADER_VERSION": "2",
        "BOARD_KERNEL_PAGESIZE": "2048",
        "BOARD_INCLUDE_DTB_IN_BOOTIMG": "true",
        "BOARD_PREBUILT_DTBIMAGE_DIR": "$(DEVICE_PATH)/prebuilt/dtb",
        "BOARD_INCLUDE_RECOVERY_DTBO": "true",
        "BOARD_PREBUILT_DTBOIMAGE": "$(DEVICE_PATH)/prebuilt/recovery_dtbo.img",
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE": str(RECOVERY_PARTITION_SIZE),
        "BOARD_SUPER_PARTITION_SIZE": str(SUPER_PARTITION_SIZE),
        "PLATFORM_SECURITY_PATCH": SECURITY_PATCH,
        "VENDOR_SECURITY_PATCH": SECURITY_PATCH,
        "BOARD_USES_METADATA_PARTITION": "true",
        "BOARD_SUPER_PARTITION_GROUPS": "main",
        "BOARD_MAIN_SIZE": str(DYNAMIC_GROUP_SIZE),
        "BOARD_MAIN_PARTITION_LIST": DYNAMIC_PARTITIONS,
        "BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE": "f2fs",
        "TARGET_USERIMAGES_USE_EXT4": "true",
        "TARGET_USERIMAGES_USE_F2FS": "true",
        "TARGET_RECOVERY_FSTAB": "$(DEVICE_PATH)/recovery.fstab",
        "TW_THEME": "portrait_hdpi",
        "TW_DEFAULT_LANGUAGE": "vi",
        "TW_EXTRA_LANGUAGES": "true",
        "TW_USE_TOOLBOX": "true",
        "TW_SCREEN_BLANK_ON_BOOT": "true",
        "TW_INPUT_BLACKLIST": "hbtp_vm",
    }
    for key, value in values.items():
        content = set_make_var(content, key, value)

    content = insert_before(content, "ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)", {
        "TARGET_FORCE_PREBUILT_KERNEL": "true",
        "TARGET_PREBUILT_KERNEL": "$(DEVICE_PATH)/prebuilt/kernel",
    })
    content = patch_mkbootimg_args(content)
    board.write_text(re.sub(r"\n{3,}", "\n\n", content), encoding="utf-8")


def patch_device_mk(device_dir):
    path = device_dir / "device.mk"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    content = remove_make_vars(content, {"LOCAL_PATH", "PRODUCT_USE_DYNAMIC_PARTITIONS", "PRODUCT_SHIPPING_API_LEVEL"})
    content = set_make_var(content, "LOCAL_PATH", "$(call my-dir)")
    content = set_make_var(content, "PRODUCT_USE_DYNAMIC_PARTITIONS", "true")
    content = set_make_var(content, "PRODUCT_SHIPPING_API_LEVEL", "29")
    path.write_text(content, encoding="utf-8")


def patch_product(device_dir):
    candidates = list(device_dir.glob("omni_*.mk")) + list(device_dir.glob("twrp_*.mk"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one Omni/TWRP product file, found {len(candidates)}")
    old_path = candidates[0]
    new_path = device_dir / "twrp_apollo2.mk"
    content = old_path.read_text(encoding="utf-8")
    content = content.replace("vendor/omni/config/common.mk", "vendor/twrp/config/common.mk")
    content = content.replace("omni_apollo2", "twrp_apollo2")
    values = {
        "PRODUCT_DEVICE": DEVICE,
        "PRODUCT_NAME": "twrp_apollo2",
        "PRODUCT_BRAND": "Alcatel",
        "PRODUCT_MODEL": "9032X",
        "PRODUCT_MANUFACTURER": "TCL",
        "PRIVATE_BUILD_DESC": f'"{STOCK_BUILD_DESC}"',
        "BUILD_FINGERPRINT": STOCK_FINGERPRINT,
    }
    for key, value in values.items():
        content = set_make_var(content, key, value)
    new_path.write_text(content, encoding="utf-8")
    if old_path != new_path:
        old_path.unlink()
    return new_path


def patch_registration(device_dir):
    (device_dir / "AndroidProducts.mk").write_text(
        "PRODUCT_MAKEFILES := \\\n    $(LOCAL_DIR)/twrp_apollo2.mk\n\n"
        "COMMON_LUNCH_CHOICES := \\\n    twrp_apollo2-eng\n",
        encoding="utf-8",
    )
    setup = device_dir / "vendorsetup.sh"
    setup.write_text(
        "#!/bin/bash\n"
        "export TARGET_ARCH=arm\n"
        "export FOX_BUILD_DEVICE=apollo2\n"
        "export FOX_VANILLA_BUILD=1\n"
        "export OF_FORCE_PREBUILT_KERNEL=1\n"
        "export FOX_REMOVE_AAPT=1\n"
        "add_lunch_combo twrp_apollo2-eng\n",
        encoding="utf-8",
    )
    setup.chmod(0o755)


def patch_fstab(device_dir):
    path = device_dir / "recovery.fstab"
    if not path.is_file():
        raise RuntimeError("recovery.fstab is missing")
    kept = []
    metadata = []
    userdata = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            kept.append(line)
            continue
        if any(token in line.lower() for token in INVALID_PARTITIONS):
            continue
        fields = stripped.split()
        if len(fields) < 3:
            kept.append(line)
            continue
        if fields[0] == "/metadata":
            fields[2] = "/dev/block/mmcblk0p16"
            metadata.append(fields)
            line = " ".join(fields)
        elif fields[1] == "/metadata":
            fields[0] = "/dev/block/mmcblk0p16"
            metadata.append(fields)
            line = " ".join(fields)
        if fields[0] == "/data":
            userdata.append(fields[1].lower())
        elif fields[1] == "/data":
            userdata.append(fields[2].lower())
        kept.append(line)
    if len(metadata) != 1:
        raise RuntimeError(f"Expected one /metadata row, found {len(metadata)}")
    if userdata != ["f2fs"]:
        raise RuntimeError(f"/data must have exactly one F2FS row, got {userdata}")
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def patch_init(device_dir):
    path = device_dir / "recovery/root/init.recovery.mt6761.rc"
    if not path.is_file():
        raise RuntimeError("init.recovery.mt6761.rc is missing")
    content = path.read_text(encoding="utf-8")
    if "import /init.recovery.smartlog.rc" in content and not list(device_dir.rglob("init.recovery.smartlog.rc")):
        content = re.sub(
            r"^[ \t]*import /init\.recovery\.smartlog\.rc[ \t]*$",
            "# Optional stock smartlog init file is absent.",
            content,
            flags=re.MULTILINE,
        )
        path.write_text(content, encoding="utf-8")


def write_report(device_dir):
    lines = [
        "GernalOS Lite OrangeFox device-tree preparation report",
        "",
        f"Device tree: {DEVICE_PATH}",
        "Device: Alcatel 9032X / Apollo_8_4G; internal codename apollo2",
        "Stock platform: MT6761; Android 10 / API 29",
        "Userspace: ARM32 armeabi-v7a; kernel: Linux 4.9.190+",
        f"Fingerprint: {STOCK_FINGERPRINT}",
        f"Security patch: {SECURITY_PATCH}",
        f"Recovery partition limit: {RECOVERY_PARTITION_SIZE} bytes",
        f"Super partition: {SUPER_PARTITION_SIZE} bytes",
        f"Dynamic group main: {DYNAMIC_GROUP_SIZE} bytes",
        f"Dynamic logical partitions: {DYNAMIC_PARTITIONS}",
        "Metadata mount: /dev/block/mmcblk0p16 (md_udc)",
        "Userdata: F2FS",
        "Boot image header: v2; page size: 2048 bytes",
        "Stock kernel, DTB, and recovery-DTBO payloads are size-checked.",
        "FBE decryption is deferred and not enabled or claimed.",
        "Vietnamese is selected as the default UI language; the build must supply a valid vi.xml resource.",
        "The Dark visual style remains a first-boot/UI Center target; no unverified theme-default variable is invented.",
        "OrangeFox FOX_* variables are exported from vendorsetup.sh.",
        "A/B mode is not enabled because the slot layout has not been conclusively established.",
        "No image has been compiled, boot-tested, or flashed by this script.",
    ]
    (device_dir / "DEVICE_TREE_FIX_REPORT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_tree(device_dir, board_path, product_path):
    board = board_path.read_text(encoding="utf-8")
    required = {
        "TARGET_BOARD_PLATFORM": "mt6761",
        "TARGET_ARCH": "arm",
        "TARGET_ARCH_VARIANT": "armv7-a-neon",
        "TARGET_CPU_ABI": "armeabi-v7a",
        "TARGET_USES_64_BIT_BINDER": "false",
        "BOARD_BOOTIMG_HEADER_VERSION": "2",
        "BOARD_KERNEL_PAGESIZE": "2048",
        "BOARD_INCLUDE_DTB_IN_BOOTIMG": "true",
        "BOARD_PREBUILT_DTBIMAGE_DIR": "$(DEVICE_PATH)/prebuilt/dtb",
        "BOARD_INCLUDE_RECOVERY_DTBO": "true",
        "BOARD_PREBUILT_DTBOIMAGE": "$(DEVICE_PATH)/prebuilt/recovery_dtbo.img",
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE": str(RECOVERY_PARTITION_SIZE),
        "BOARD_SUPER_PARTITION_SIZE": str(SUPER_PARTITION_SIZE),
        "PLATFORM_SECURITY_PATCH": SECURITY_PATCH,
        "VENDOR_SECURITY_PATCH": SECURITY_PATCH,
        "BOARD_MAIN_SIZE": str(DYNAMIC_GROUP_SIZE),
        "TW_DEFAULT_LANGUAGE": "vi",
        "TW_EXTRA_LANGUAGES": "true",
    }
    for key, value in required.items():
        if not re.search(rf"^[ \t]*{re.escape(key)}[ \t]*:=\s*{re.escape(value)}\s*$", board, re.MULTILINE):
            raise RuntimeError(f"BoardConfig validation failed: {key}")
    if "--dtb $(TARGET_PREBUILT_DTB)" in board or "2099-12-31" in board or "16.1.0" in board:
        raise RuntimeError("Obsolete DTB/security/platform setting remains")
    if len(re.findall(r"BOARD_MKBOOTIMG_ARGS\s*\+=\s*--header_version", board)) != 1:
        raise RuntimeError("Expected one --header_version argument")
    for key in ("TW_INCLUDE_CRYPTO", "TW_INCLUDE_CRYPTO_FBE", "TW_INCLUDE_FBE", "TW_INCLUDE_FBE_METADATA_DECRYPT"):
        if assignment_pattern(key).search(board):
            raise RuntimeError(f"FBE must remain deferred: {key}")
    if re.search(r"^[ \t]*BOARD_AVB_(ENABLE|RECOVERY_KEY_PATH|RECOVERY_ALGORITHM|RECOVERY_ROLLBACK_INDEX|RECOVERY_ROLLBACK_INDEX_LOCATION)[ \t]*(?::=|\?=|\+=)", board, re.MULTILINE):
        raise RuntimeError("Do not use an unverified OEM AVB signing key")
    if assignment_pattern("BOARD_BOOTIMAGE_PARTITION_SIZE").search(board):
        raise RuntimeError("Boot partition size has not been verified")

    product = product_path.read_text(encoding="utf-8")
    for key, value in {
        "PRODUCT_DEVICE": DEVICE,
        "PRODUCT_NAME": "twrp_apollo2",
        "PRODUCT_BRAND": "Alcatel",
        "PRODUCT_MODEL": "9032X",
        "PRODUCT_MANUFACTURER": "TCL",
        "BUILD_FINGERPRINT": STOCK_FINGERPRINT,
    }.items():
        if not re.search(rf"^[ \t]*{key}[ \t]*:=\s*{re.escape(value)}\s*$", product, re.MULTILINE):
            raise RuntimeError(f"Product validation failed: {key}")
    if "vendor/twrp/config/common.mk" not in product:
        raise RuntimeError("TWRP/OrangeFox common product configuration is not inherited")

    registration = (device_dir / "AndroidProducts.mk").read_text(encoding="utf-8")
    setup = (device_dir / "vendorsetup.sh").read_text(encoding="utf-8")
    if "twrp_apollo2-eng" not in registration or "FOX_BUILD_DEVICE=apollo2" not in setup:
        raise RuntimeError("OrangeFox lunch target/build setup is missing")
    if "FOX_AB_DEVICE" in setup:
        raise RuntimeError("A/B mode must not be assumed")
    if not re.search(r"PRODUCT_USE_DYNAMIC_PARTITIONS\s*:=\s*true", (device_dir / "device.mk").read_text(encoding="utf-8")):
        raise RuntimeError("Dynamic partitions are not enabled")

    fstab = (device_dir / "recovery.fstab").read_text(encoding="utf-8")
    active = [x for x in fstab.splitlines() if x.strip() and not x.lstrip().startswith("#")]
    metadata = [x for x in active if re.search(r"(^|\s)/metadata(\s|$)", x)]
    data = [x for x in active if re.search(r"(^|\s)/data(\s|$)", x)]
    if len(metadata) != 1 or "/dev/block/mmcblk0p16" not in metadata[0]:
        raise RuntimeError("Metadata must map to md_udc on mmcblk0p16")
    if len(data) != 1 or not re.search(r"\bf2fs\b", data[0]):
        raise RuntimeError("Userdata must use F2FS")
    if any(name in "\n".join(active).lower() for name in INVALID_PARTITIONS):
        raise RuntimeError("An unsupported/nonexistent fstab partition remains")

    for relative, expected in EXPECTED_FILES.items():
        path = device_dir / "prebuilt" / relative
        if not path.is_file() or path.stat().st_size != expected:
            raise RuntimeError(f"Prebuilt payload invalid: {relative}")


def fix_tree(root):
    if not root.is_dir():
        raise RuntimeError(f"Device tree root does not exist: {root}")
    board = normalize_device_path(find_board(root))
    device_dir = board.parent
    replace_device_paths(device_dir)
    normalize_prebuilt(device_dir)
    patch_board(board)
    patch_device_mk(device_dir)
    product = patch_product(device_dir)
    patch_registration(device_dir)
    patch_fstab(device_dir)
    patch_init(device_dir)
    write_report(device_dir)
    validate_tree(device_dir, board, product)
    print(f"Prepared OrangeFox device tree: {device_dir}")
    print("Validation: passed")
    return device_dir


def main():
    parser = argparse.ArgumentParser(description="Prepare and validate Alcatel 9032X OrangeFox device tree")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    fix_tree(args.root)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"OrangeFox device-tree preparation failed: {error}")
