# GernalOS Lite — OrangeFox Port Plan

## Release target

**GernalOS Lite Alpha 1 – Fox Dark Vietnamese**

- Device: Alcatel 9032X / Apollo_8_4G
- Device-tree codename: apollo2
- Device-tree path: device/tcl/apollo2
- OrangeFox interface: Dark appearance, selected through UI Center until a verified default-theme mechanism is available
- Language: Vietnamese (vi) by default, only with a valid vi.xml resource
- Architecture: ARM32
- First milestone: boot successfully; FBE is deferred
- Recovery image limit: exactly 33,554,432 bytes (32 MiB)

## Verified device data from the previous device investigation

| Item | Confirmed value |
|---|---|
| Stock Android | Android 10 / SDK 29 |
| Android platform target | MT6761 |
| Userspace ABI | armeabi-v7a, armeabi |
| CPU runtime variant | Cortex-A53 |
| Kernel | Linux 4.9.190+ |
| Boot image header | v2 |
| Kernel page size | 2048 bytes |
| Stock recovery size | 33,554,432 bytes |
| Recovery partitions | recovery and recovery2, 32 MiB each |
| Compressed kernel payload | 8,637,050 bytes |
| DTB payload | 78,570 bytes |
| Recovery DTBO payload | 60,296 bytes |
| Userdata filesystem | F2FS |
| Super partition | 4,949,278,720 bytes |
| Dynamic group maximum | 4,947,181,568 bytes |
| Logical partitions | system, vendor, product, odm, oem |
| Metadata block source | md_udc, /dev/block/mmcblk0p16 |
| Stock security patch | 2021-11-05 |

Stock fingerprint:

Alcatel/9032X/Apollo_8_4G:10/QP1A.190711.020/1E24:user/release-keys

Stock recovery SHA-256:

fea18b7c5c771054aec49559b09162be56dcc504667866fb2ffed54618886c07

The build target uses the MT6761 platform evidence from Android properties and device configuration. One CPU diagnostic previously displayed a conflicting hardware label, so that line alone is not treated as proof of the silicon model.

## Device-tree corrections now applied in this branch

- Corrected stale security patch values from 2099-12-31 to 2021-11-05.
- Removed stale TWRP compatibility version 16.1.0 from the generated BoardConfig.
- Set ARM32, MT6761, Cortex-A53, and stock prebuilt kernel values.
- Kept the prebuilt kernel, DTB, and recovery-DTBO as separate verified payloads.
- Arranged DTB handling through BOARD_INCLUDE_DTB_IN_BOOTIMG and BOARD_PREBUILT_DTBIMAGE_DIR.
- Arranged recovery-DTBO handling through BOARD_INCLUDE_RECOVERY_DTBO and BOARD_PREBUILT_DTBOIMAGE.
- Kept the Android boot header version 2 and 2048-byte page size.
- Kept recovery image partition limit at 32 MiB.
- Kept super partition size, dynamic group size, and logical partition list from device lpdump data.
- Kept /metadata mapped to md_udc at mmcblk0p16, not the separate metadata partition.
- Required /data to remain F2FS.
- Removed unsupported fstab rows for md1dsp, md1arm7, md3img, and odmdtbo.
- Removed unverified AVB signing settings.
- Deferred FBE build/decryption flags.
- Kept OrangeFox FOX_* variables in vendorsetup.sh.

These are device-tree preparation changes. They are not proof that the resulting OrangeFox image will boot.

## OrangeFox source branch

The CI currently tries official fox_12.1 because the official sync project currently documents 12.1 and 14.1, while 14.1 is described primarily for devices launched on Android 14 or later. This tablet shipped with Android 10. Therefore fox_12.1 is a candidate to test, not a branch/device compatibility result. If the build fails due to old Android 10 platform compatibility, reassess the base branch instead of patching around unknown errors.

The build uses Python 2.7 as the default Python for legacy steps and Java 8 for fox_12.1, FOX_VANILLA_BUILD for a non-Xiaomi tablet, and OF_FORCE_PREBUILT_KERNEL for the prebuilt stock kernel path. Do not set FOX_AB_DEVICE unless A/B status is proven. The current investigation did not prove A/B status.

## Vietnamese interface and Dark theme

- Keep extra-language resources enabled until the Vietnamese file is checked.
- Require a real languages/vi.xml resource in the synced source.
- CI must stop if vi.xml is absent; do not silently create a fake translation or ship an English UI labelled Vietnamese.
- Keep terminal input, shell output, paths, block-device names, and command syntax in English.
- Use the OrangeFox Dark style through UI Center after the first successful boot unless a branch-specific default theme mechanism is verified. Do not invent a theme variable.

## Lite feature scope

Keep for the first milestone:

- Main graphical recovery interface
- Install ZIP
- Wipe
- Mount
- Reboot
- Integrated terminal
- ADB shell and ADB sideload
- Recovery logs and core shell tools
- F2FS and ext4 support needed by the device

Keep if image size and testing permit:

- Backup and Restore
- File manager

Defer:

- FBE decryption
- Unneeded language packs (without removing Vietnamese)
- LZMA compression until the kernel's support is proven
- Experimental drastic size reduction
- Unneeded filesystem drivers and optional large utilities

## Alpha 1 acceptance checklist

- [ ] CI preparation tests pass.
- [ ] OrangeFox source sync succeeds.
- [ ] A genuine Vietnamese translation resource is included.
- [ ] OrangeFox compiles for the Apollo2 target.
- [ ] Output image is valid Android boot header v2.
- [ ] Output image is at most 33,554,432 bytes.
- [ ] First boot succeeds without kernel panic or boot loop.
- [ ] Display and touchscreen work.
- [ ] Vietnamese text renders correctly.
- [ ] Dark theme can be selected and retained.
- [ ] Integrated terminal runs basic shell commands.
- [ ] ADB shell connects from a PC.
- [ ] Required partitions can be identified and mounted safely.
- [ ] Reboot behavior is verified.
- [ ] Backup/Restore is tested if included.
- [ ] FBE decryption is tested separately before any claim is made.
- [ ] Stock recovery and boot restoration path is confirmed before any flash test.

## Safety boundary

Do not flash recovery or recovery2 merely because the image compiled or passed a size check. A successful compile is not a boot test. Use the existing stock backups and a controlled non-flashing boot test first. No test image has been flashed to this tablet by this project.
