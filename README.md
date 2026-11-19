# Alcatel 9032X / Apollo_8_4G TWRP bring-up

Target device: Alcatel 9032X, device codename Apollo_8_4G, internal build codename `apollo2`.

## Verified device profile

- SoC: MediaTek MT6761
- Stock Android: Android 10 / SDK 29 / first API level 29
- Kernel and userspace: 32-bit ARM (ARMv7-A with NEON, `armeabi-v7a`)
- CPU runtime variant: Cortex-A53
- Boot image header: v2
- Kernel page size: 2048 bytes
- Stock recovery image: 33,554,432 bytes
- Recovery partition: 33,554,432 bytes
- Userdata filesystem: F2FS
- Super partition: 4,949,278,720 bytes
- Metadata mount source observed on the running tablet: `/dev/block/mmcblk0p16`
- Stock fingerprint: `Alcatel/9032X/Apollo_8_4G:10/QP1A.190711.020/1E24:user/release-keys`

The stock recovery image is stored in the GitHub Release tagged `Recovery`. The workflow checks both its SHA-256 and exact size before extraction.

## What the workflow fixes

The workflow first generates a device tree from the stock recovery image, then runs `scripts/fix_device_tree.py` to apply and validate device-specific corrections:

- Renames the generated manufacturer folder from `alps` to `tcl`, matching the device's reported manufacturer while retaining the confirmed internal codename `apollo2`.
- Sets the build target to ARM32 and MT6761, and removes generated secondary-architecture and kernel-source references that do not match this prebuilt-kernel tree.
- Keeps the stock kernel, DTB, and DTBO prebuilt files and checks their expected sizes before uploading the result.
- Sets the recovery image partition size to 32 MiB. It does not hardcode the separate boot partition size because that partition size has not been verified.
- Sets the physical super partition size to 4,949,278,720 bytes and the `main` group maximum to 4,947,181,568 bytes, both read directly from the device's `lpdump` output. The actual group name is `main`; no guessed 4 MiB reserve is used.
- Sets the dynamic partition list to `system vendor product odm oem` and enables dynamic partitions in `device.mk`.
- Uses the observed metadata block device `/dev/block/mmcblk0p16` in the recovery fstab.
- Enables TWRP FBE/metadata-decryption build features because the stock system reports `ro.crypto.type=file`; actual decryption remains unverified until the stock userdata fstab and MediaTek Keymaster dependencies are checked.
- Sets the product identity to Alcatel / TCL / 9032X while keeping the internal product codename.
- Removes the import of the optional `init.recovery.smartlog.rc` only when that file is absent from the extracted recovery tree.

AVB signing variables are removed from the test device tree because the OEM recovery private key is unavailable. The extracted 520-byte public key cannot sign an image, and the AOSP test key would not match the OEM chain descriptor. Any first test must use `fastboot boot` with the bootloader unlocked; it must not be flashed to the recovery partition.\n\nThe generated TWRP compatibility values `PLATFORM_VERSION := 16.1.0` and security patch `2099-12-31` are intentionally preserved. They are commonly used by TWRP device trees as build/rollback compatibility settings and are not the stock Android version or the stock security patch. The prebuilt-kernel variables are placed before their `ifeq` block so the stock kernel, DTB, and DTBO settings are actually selected during make evaluation.

## Run the corrected preflight

1. Open the repository's **Actions** tab.
2. Select **TWRP Device Tree Fix and Preflight**.
3. Choose **Run workflow** on branch `master`.
4. Keep the default image URL and SHA-256.
5. Start the workflow.
6. Download the artifact named `alcatel-9032x-device-tree-fixed`.

## Current safety boundary

This repository currently generates and validates the corrected device tree only. It does **not** compile a TWRP image and does **not** flash the tablet.

A successful preflight is not proof that a recovery will boot. Encryption/decryption, touchscreen mapping, display behavior, USB/MTP, mounting/formatting, and reboot behavior still require a controlled build-and-test cycle with verified recovery and boot backups. Do not flash a test image until those checks and the exact TWRP build branch have been completed.
