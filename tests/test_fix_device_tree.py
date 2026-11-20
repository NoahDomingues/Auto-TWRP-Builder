import tempfile
import unittest
from pathlib import Path

from scripts.fix_device_tree import fix_tree


class DeviceTreeFixTests(unittest.TestCase):
    def make_tree(self, root, metadata_line):
        device = root / "alps" / "apollo2"
        (device / "prebuilt").mkdir(parents=True)
        (device / "recovery" / "root").mkdir(parents=True)

        board = [
            "DEVICE_PATH := device/alps/apollo2",
            "TARGET_ARCH := arm",
            "TARGET_USES_64_BIT_BINDER := true",
            "TARGET_KERNEL_SOURCE := kernel/alps/apollo2",
            "TARGET_FORCE_PREBUILT_KERNEL := false",
            "ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)",
            "BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB) --header_version 2",
            "BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img",
            "BOARD_KERNEL_SEPARATED_DTBO :=",
            "endif",
            "BOARD_RECOVERYIMAGE_PARTITION_SIZE := 33554432",
            "BOARD_AVB_ENABLE := true",
            "BOARD_SUPER_PARTITION_SIZE := 9126805504",
            "BOARD_SUPER_PARTITION_GROUPS := alps_dynamic_partitions",
            "BOARD_ALPS_DYNAMIC_PARTITIONS_SIZE := 9122611200",
            "PLATFORM_SECURITY_PATCH := 2099-12-31",
            "VENDOR_SECURITY_PATCH := 2099-12-31",
            "TW_INCLUDE_CRYPTO := true",
            "TW_INCLUDE_CRYPTO_FBE := true",
            "TW_INCLUDE_FBE_METADATA_DECRYPT := true",
            "PLATFORM_VERSION := 16.1.0",
            "",
        ]
        (device / "BoardConfig.mk").write_text("\n".join(board), encoding="utf-8")
        (device / "omni_apollo2.mk").write_text(
            "\n".join([
                "$(call inherit-product, vendor/omni/config/common.mk)",
                "PRODUCT_DEVICE := apollo2",
                "PRODUCT_NAME := omni_apollo2",
                "PRODUCT_BRAND := alps",
                "PRODUCT_MODEL := apollo2",
                "PRODUCT_MANUFACTURER := alps",
                'PRIVATE_BUILD_DESC := "full_apollo2-user 10 QP1A.190711.020 1E24 release-keys"',
                "BUILD_FINGERPRINT := None",
                "",
            ]),
            encoding="utf-8",
        )
        (device / "device.mk").write_text("LOCAL_PATH := device/alps/apollo2\n", encoding="utf-8")
        (device / "recovery.fstab").write_text(
            metadata_line + "\n/dev/block/platform/bootdevice/by-name/userdata /data f2fs defaults\n"
            "/dev/block/platform/bootdevice/by-name/md1dsp /md1dsp ext4 defaults\n",
            encoding="utf-8",
        )
        (device / "recovery" / "root" / "init.recovery.mt6761.rc").write_text(
            "import /init.recovery.smartlog.rc\non boot\n    setprop ro.debuggable 1\n",
            encoding="utf-8",
        )
        for name, size in (("kernel", 8637050), ("dtb.img", 78570), ("dtbo.img", 60296)):
            with (device / "prebuilt" / name).open("wb") as stream:
                stream.truncate(size)
        return device

    def test_normalizes_stock_components_and_orangefox_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root, "/dev/block/platform/bootdevice/by-name/md_udc /metadata ext4 defaults")
            device = fix_tree(root)
            board = (device / "BoardConfig.mk").read_text(encoding="utf-8")
            product = (device / "twrp_apollo2.mk").read_text(encoding="utf-8")
            fstab = (device / "recovery.fstab").read_text(encoding="utf-8")
            setup = (device / "vendorsetup.sh").read_text(encoding="utf-8")

            self.assertEqual(device.relative_to(root).as_posix(), "tcl/apollo2")
            self.assertIn("BOARD_SUPER_PARTITION_SIZE := 4949278720", board)
            self.assertIn("BOARD_MAIN_SIZE := 4947181568", board)
            self.assertIn("BOARD_INCLUDE_DTB_IN_BOOTIMG := true", board)
            self.assertIn("BOARD_INCLUDE_RECOVERY_DTBO := true", board)
            self.assertIn("PLATFORM_SECURITY_PATCH := 2021-11-05", board)
            self.assertIn("TW_DEFAULT_LANGUAGE := vi", board)
            self.assertNotIn("2099-12-31", board)
            self.assertNotIn("16.1.0", board)
            self.assertNotIn("TW_INCLUDE_CRYPTO", board)
            self.assertNotIn("--dtb $(TARGET_PREBUILT_DTB)", board)
            self.assertIn("vendor/twrp/config/common.mk", product)
            self.assertIn("PRODUCT_MANUFACTURER := TCL", product)
            self.assertIn("PRODUCT_BRAND := Alcatel", product)
            self.assertIn("/dev/block/mmcblk0p16 /metadata", fstab)
            self.assertNotIn("md1dsp", fstab)
            self.assertIn("/data f2fs", fstab)
            self.assertIn("FOX_BUILD_DEVICE=apollo2", setup)
            self.assertNotIn("FOX_AB_DEVICE", setup)
            self.assertTrue((device / "prebuilt/dtb/mt6761.dtb").is_file())
            self.assertTrue((device / "prebuilt/recovery_dtbo.img").is_file())

    def test_mountpoint_first_metadata_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root, "/metadata ext4 /dev/block/platform/bootdevice/by-name/md_udc flags=display=Metadata")
            device = fix_tree(root)
            fstab = (device / "recovery.fstab").read_text(encoding="utf-8")
            self.assertIn("/metadata ext4 /dev/block/mmcblk0p16", fstab)

    def test_rejects_non_f2fs_userdata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = self.make_tree(root, "/dev/block/platform/bootdevice/by-name/md_udc /metadata ext4 defaults")
            fstab = device / "recovery.fstab"
            fstab.write_text(
                fstab.read_text(encoding="utf-8").replace("/data f2fs", "/data ext4"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "F2FS"):
                fix_tree(root)

    def test_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root, "/dev/block/platform/bootdevice/by-name/md_udc /metadata ext4 defaults")
            first = fix_tree(root)
            second = fix_tree(root)
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
