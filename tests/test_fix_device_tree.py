import tempfile
import unittest
from pathlib import Path

from scripts.fix_device_tree import fix_tree


class DeviceTreeFixTests(unittest.TestCase):
    def make_tree(self, root: Path, metadata_line: str) -> Path:
        device = root / "alps" / "apollo2"
        (device / "prebuilt").mkdir(parents=True)
        (device / "recovery" / "root").mkdir(parents=True)

        (device / "BoardConfig.mk").write_text(
            "\n".join(
                [
                    "DEVICE_PATH := device/alps/apollo2",
                    "TARGET_ARCH := arm",
                    "TARGET_ARCH_VARIANT := armv7-a-neon",
                    "TARGET_CPU_ABI := armeabi-v7a",
                    "TARGET_CPU_ABI2 := armeabi",
                    "TARGET_CPU_VARIANT_RUNTIME := cortex-a53",
                    "TARGET_USES_64_BIT_BINDER := true",
                    "TARGET_KERNEL_SOURCE := kernel/alps/apollo2",
                    "TARGET_FORCE_PREBUILT_KERNEL := false",
                    "ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)",
                    "BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)",
                    "BOARD_INCLUDE_DTB_IN_BOOTIMG :=",
                    "BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img",
                    "BOARD_KERNEL_SEPARATED_DTBO :=",
                    "endif",
                    "BOARD_RECOVERYIMAGE_PARTITION_SIZE := 33554432",
                    "BOARD_SUPER_PARTITION_SIZE := 9126805504",
                    "BOARD_SUPER_PARTITION_GROUPS := alps_dynamic_partitions",
                    "BOARD_ALPS_DYNAMIC_PARTITIONS_SIZE := 9122611200",
                    "BOARD_ALPS_DYNAMIC_PARTITIONS_PARTITION_LIST := system vendor product odm oem",
                    "PLATFORM_SECURITY_PATCH := 2099-12-31",
                    "VENDOR_SECURITY_PATCH := 2099-12-31",
                    "PLATFORM_VERSION := 16.1.0",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (device / "omni_apollo2.mk").write_text(
            "\n".join(
                [
                    "PRODUCT_DEVICE := apollo2",
                    "PRODUCT_NAME := omni_apollo2",
                    "PRODUCT_BRAND := alps",
                    "PRODUCT_MODEL := apollo2",
                    "PRODUCT_MANUFACTURER := alps",
                    'PRIVATE_BUILD_DESC := "full_apollo2-user 10 QP1A.190711.020 1E24 release-keys"',
                    "BUILD_FINGERPRINT := None",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (device / "device.mk").write_text("LOCAL_PATH := device/alps/apollo2\n", encoding="utf-8")
        (device / "recovery.fstab").write_text(
            metadata_line + "\n/dev/block/platform/bootdevice/by-name/userdata /data f2fs defaults\n",
            encoding="utf-8",
        )
        (device / "recovery" / "root" / "init.recovery.mt6761.rc").write_text(
            "import /init.recovery.smartlog.rc\non boot\n    setprop ro.debuggable 1\n",
            encoding="utf-8",
        )

        for name, size in (("kernel", 8637050), ("dtb.img", 78570), ("dtbo.img", 60296)):
            with (device / "prebuilt" / name).open("wb") as handle:
                handle.truncate(size)
        return device

    def test_fixes_source_first_metadata_fstab(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_tree(
                root,
                "/dev/block/platform/bootdevice/by-name/md_udc /metadata ext4 defaults",
            )
            result = fix_tree(root)

            board = (result / "BoardConfig.mk").read_text(encoding="utf-8")
            product = (result / "omni_apollo2.mk").read_text(encoding="utf-8")
            fstab = (result / "recovery.fstab").read_text(encoding="utf-8")
            device_mk = (result / "device.mk").read_text(encoding="utf-8")
            init = (result / "recovery" / "root" / "init.recovery.mt6761.rc").read_text(encoding="utf-8")

            self.assertEqual(result.relative_to(root).as_posix(), "tcl/apollo2")
            self.assertIn("BOARD_SUPER_PARTITION_SIZE := 4949278720", board)
            self.assertIn("BOARD_SUPER_PARTITION_GROUPS := main", board)
            self.assertIn("BOARD_MAIN_SIZE := 4947181568", board)
            self.assertIn("BOARD_MAIN_PARTITION_LIST := system vendor product odm oem", board)
            self.assertNotIn("BOARD_ALPS_DYNAMIC_PARTITIONS_SIZE", board)
            self.assertIn("TARGET_USES_64_BIT_BINDER := false", board)
            self.assertNotIn("TARGET_KERNEL_SOURCE", board)
            self.assertIn("TW_INCLUDE_CRYPTO := true", board)
            self.assertIn("TW_INCLUDE_CRYPTO_FBE := true", board)
            self.assertIn("TW_INCLUDE_FBE_METADATA_DECRYPT := true", board)
            self.assertIn("BOARD_USES_METADATA_PARTITION := true", board)
            self.assertNotIn("BOARD_BOOTIMAGE_PARTITION_SIZE", board)
            self.assertLess(
                board.index("TARGET_FORCE_PREBUILT_KERNEL := true"),
                board.index("ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)"),
            )
            self.assertIn("BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img", board)
            self.assertIn("PRODUCT_MANUFACTURER := TCL", product)
            self.assertIn("PRODUCT_BRAND := Alcatel", product)
            self.assertIn("/dev/block/mmcblk0p16 /metadata", fstab)
            self.assertIn("PRODUCT_USE_DYNAMIC_PARTITIONS := true", device_mk)
            self.assertNotIn("import /init.recovery.smartlog.rc", init)
            self.assertTrue((result / "DEVICE_TREE_FIX_REPORT.txt").is_file())

    def test_fixes_mountpoint_first_metadata_fstab(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_tree(
                root,
                "/metadata ext4 /dev/block/platform/bootdevice/by-name/md_udc flags=display=Metadata",
            )
            result = fix_tree(root)
            fstab = (result / "recovery.fstab").read_text(encoding="utf-8")
            self.assertIn("/metadata ext4 /dev/block/mmcblk0p16", fstab)


if __name__ == "__main__":
    unittest.main()
