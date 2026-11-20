# GernalOS Lite — OrangeFox port for Alcatel 9032X

This branch prepares an unofficial OrangeFox recovery port for the Alcatel 9032X (Apollo_8_4G). The first target is **GernalOS Lite Alpha 1 – Fox Dark Vietnamese**.

> **Status:** device-tree preparation and CI build workflow are in progress. No OrangeFox image has been confirmed to compile, boot, or operate on the tablet. Do not flash an artifact just because CI produces it.

## Verified device profile

- Product: Alcatel 9032X / Apollo_8_4G
- Internal device-tree codename: apollo2
- Device-tree path: device/tcl/apollo2
- Android stock base: Android 10 / API 29
- Platform reported by device properties and fstab: MT6761
- Userspace: 32-bit ARM, armeabi-v7a / armeabi
- CPU runtime variant reported by Android: Cortex-A53
- Kernel: Linux 4.9.190+
- Boot image header: v2
- Kernel page size: 2048 bytes
- Recovery and recovery2 partitions: 33,554,432 bytes each (32 MiB)
- Stock recovery image backup size: 33,554,432 bytes
- Stock recovery SHA-256: fea18b7c5c771054aec49559b09162be56dcc504667866fb2ffed54618886c07
- Stock fingerprint: Alcatel/9032X/Apollo_8_4G:10/QP1A.190711.020/1E24:user/release-keys
- Stock security patch: 2021-11-05
- Userdata filesystem: F2FS
- Super partition: 4,949,278,720 bytes
- Dynamic partition group main maximum: 4,947,181,568 bytes
- Logical partitions: system, vendor, product, odm, oem
- Metadata mount source: /dev/block/mmcblk0p16 (md_udc)

The platform evidence identifies MT6761 in Android properties and device configuration. A different hardware label was previously seen in one CPU diagnostic, so the platform value is recorded as the build target, not presented as a standalone silicon proof.

## Stock recovery components

The stock recovery header inspection recorded these component sizes:

- Compressed kernel payload: 8,637,050 bytes
- DTB: 78,570 bytes
- Recovery DTBO: 60,296 bytes
- Boot image header version: 2
- Page size: 2048 bytes

The preparation script checks the generated prebuilt payload sizes before it allows the tree to continue. The decompressed kernel size is not the same as the compressed kernel payload size.

## Safety decisions

- The image must never exceed the 32 MiB recovery partition.
- /metadata is kept on md_udc at mmcblk0p16. The separate partition named metadata is not substituted.
- /data stays F2FS.
- Unsupported fstab rows for md1dsp, md1arm7, md3img, and odmdtbo are removed.
- FBE decryption is deferred. Stock Android uses file-based encryption, but recovery decryption has not been proven with the tablet's Keymaster components and a real credential.
- No OEM AVB private key is available. Do not sign with an unrelated test key.
- A/B mode is not enabled. The existence of recovery and recovery2 partitions does not, by itself, prove the OrangeFox A/B configuration.
- No boot partition size is invented.
- No test image is flashed by CI.

## OrangeFox build choice

The CI workflow currently attempts the official OrangeFox fox_12.1 source branch. The current OrangeFox sync project documents branches 12.1 and 14.1; its build guide associates 12.1 with Android 12+ devices and 14.1 mostly with devices launched on Android 14+. This Alcatel shipped with Android 10, so fox_12.1 is a **candidate build experiment**, not a proven compatibility match. A successful compile must still be checked on the target device.

The OrangeFox build guide requires Python 2.7 as the default Python for legacy build steps, recommends Java 8 for the fox_12.1 build variables, says to use FOX_VANILLA_BUILD for non-Xiaomi devices, and recommends OF_FORCE_PREBUILT_KERNEL when a prebuilt kernel causes a NO KERNEL CONFIG error. OrangeFox-specific FOX variables are supplied from vendorsetup.sh, not BoardConfig.mk.

The first build uses a prebuilt stock kernel and does not enable LZMA ramdisk compression because kernel support has not been verified. FOX_REMOVE_AAPT is enabled as a size-saving trial; if the image or build loses a required feature, remove that option and retest.

## GernalOS Lite Alpha 1 target

Keep and validate:

- OrangeFox graphical recovery interface
- Dark appearance selected through OrangeFox UI Center; automatic first-boot theme selection has not yet been verified
- Vietnamese as the default UI language (`TW_DEFAULT_LANGUAGE := vn`), generated from the synced OrangeFox English resources
- Install ZIP, Wipe, Mount, Reboot, recovery logs
- Integrated terminal and ADB shell / ADB sideload
- F2FS and ext4 support needed by this tablet
- Backup and Restore only if the resulting image remains within 32 MiB and the feature works

Defer or disable until separately tested:

- FBE decryption
- Unneeded language packs (Vietnamese must remain available)
- Optional large tools that are not required for the first boot
- LZMA compression
- Experimental drastic size reduction
- Unverified filesystem and partition handlers

The upstream `fox_12.1` tree has the English base at `gui/theme/common/languages/en.xml` but does not provide a Vietnamese locale. The workflow generates `gui/theme/extra-languages/languages/vn.xml` from that exact base, translates the main menus/actions and retains untranslated English strings as fallbacks. CI validates the XML and required menu labels before compiling. Terminal commands, partition names, paths, and shell output remain in English/technical form.

## CI workflow

GitHub Actions workflow: .github/workflows/OrangeFox Lite Build.yml

It is intended to:

1. Verify the stock recovery image size and SHA-256.
2. Generate a starter device tree with twrpdtgen.
3. Apply Alcatel-specific corrections and run unit tests.
4. Sync OrangeFox fox_12.1 sources with the official OrangeFox sync script.
5. Confirm that a Vietnamese translation resource exists.
6. Add device/tcl/apollo2 and build an OrangeFox recovery image.
7. Verify Android boot image header v2 and the 32 MiB image-size limit.
8. Upload a CI artifact for inspection only.

The build has not yet been shown to succeed. A CI artifact, if produced, is not proof of a successful boot. First testing must use a controlled non-flashing boot method and the existing stock recovery/boot backups. Do not flash recovery or recovery2 until display, touchscreen, ADB, mounts, reboot behavior, and a recovery path have been checked.

## Source licensing

OrangeFox is GPL-3.0-or-later. Any public release containing modified OrangeFox source, vendor files, or device-tree files must publish the corresponding modified source as required by the license.
