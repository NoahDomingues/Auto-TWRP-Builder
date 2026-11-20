# GernalOS Lite — OrangeFox Port Plan

## Target

- Device: Alcatel 9032X / Apollo_8_4G
- Device-tree codename: apollo2
- Manufacturer path: device/tcl/apollo2
- UI: OrangeFox Fox Dark, Vietnamese as the default language
- Terminal: integrated GUI terminal and ADB shell
- First milestone: boot-first Alpha 1; FBE decryption is deferred
- Recovery partition limit: 33,554,432 bytes (32 MiB)

## Verified device facts

- Android stock base: Android 10 / SDK 29
- Reported platform: MT6761
- Userspace: 32-bit ARM (armeabi-v7a)
- Kernel: Linux 4.9.190
- Boot image header: v2
- Kernel page size: 2048 bytes
- Recovery and recovery2 partitions: 32 MiB each
- Userdata filesystem: F2FS
- Super partition: 4,949,278,720 bytes
- Dynamic partition group maximum: 4,947,181,568 bytes
- Dynamic logical partitions: system, vendor, product, odm, oem
- Metadata source observed in the stock vendor fstab: md_udc (mmcblk0p16)

## Important OrangeFox integration rules

1. Follow the official OrangeFox build guide and use its sync/manifest workflow.
2. Select the OrangeFox source branch only after checking its compatibility with this Android 10 device tree and its required build environment. Do not assume the branch from the TWRP workflow is automatically compatible.
3. Put OrangeFox-specific FOX_* variables in a shell script or vendorsetup.sh. Do not put FOX_* variables in BoardConfig.mk.
4. Keep TARGET_ARCH=arm and register the correct device codename for the build.
5. Do not set FOX_AB_DEVICE or vendor_boot recovery options unless the partition/slot design is conclusively verified. This device has dedicated recovery partitions; its two recovery partition names alone do not prove A/B behavior.
6. Do not enable LZMA ramdisk compression until the stock kernel's built-in LZMA decompression support is verified.
7. Consider FOX_REMOVE_AAPT only after confirming no selected installer or runtime feature requires aapt. It is documented as a potential size saving, not a default.
8. Avoid FOX_CUSTOM_BINS_TO_SDCARD and extreme size-reduction options for Alpha 1. They are experimental and may depend on internal storage/decryption.
9. Do not claim FBE decryption works. Keep it out of the first acceptance criteria and investigate Keymaster/Gatekeeper separately.
10. Do not flash a test image. First validate image format, exact size, kernel/ramdisk packing, and a recoverable test method.

## Vietnamese localization plan

- Inspect the selected OrangeFox branch's language/resource structure before changing language build flags.
- Keep the Vietnamese translation resources in the build; do not globally disable extra languages if that removes Vietnamese.
- Set Vietnamese as the default UI language only after confirming the exact language identifier and resource filenames in that branch.
- Translate visible menu labels, dialogs, settings, and error messages consistently.
- Keep terminal commands, shell output, partition names, filesystem names, and paths in their technical form.
- Verify Vietnamese diacritics render with the bundled fonts without adding large font packs unnecessarily.

## Lite GUI + Terminal feature set

Keep:
- Touchscreen GUI and Fox Dark theme
- Install ZIP
- Wipe
- Mount
- Reboot
- Integrated terminal
- ADB shell and ADB sideload
- Essential recovery logs and shell tools
- F2FS and ext4 support needed by this device

Defer or omit from Alpha 1 unless required:
- FBE decryption
- Extra language packs other than Vietnamese
- Optional large utilities that are not needed for boot, install, mount, or diagnosis
- Experimental binary relocation to internal storage

## Device-tree blockers to resolve before a build

- The current fix_device_tree.py still injects VENDOR_SECURITY_PATCH=2099-12-31 and validates it. Replace this with the verified firmware patch date 2021-11-05 or omit the variable if the selected OrangeFox branch does not require it.
- The same script currently adds a DTB argument and assumes a separate prebuilt DTBO path. Verify the exact stock recovery header components and the selected branch's mkbootimg rules before keeping either setting.
- The prebuilt named dtbo.img was copied from recovery_dtbo.img; confirm how the branch expects recovery_dtbo before wiring it into the build.
- Review recovery.fstab against actual by-name partitions. Do not add nonexistent partition entries.
- Preserve /metadata mapping to md_udc (mmcblk0p16), not the separate partition named metadata (mmcblk0p17).
- Validate the /data F2FS stanza and recovery mount behavior. FBE decryption is not a prerequisite for the first boot milestone.
- Confirm the OrangeFox product makefile, vendorsetup.sh, language resources, and terminal components for the selected branch.

## Alpha 1 acceptance criteria

- Image is a valid recovery image for the device's verified boot header.
- Image size is no greater than 33,554,432 bytes.
- Recovery boots without a kernel panic or boot loop.
- Display and touchscreen work.
- Fox Dark UI renders Vietnamese text correctly.
- Integrated terminal opens and executes basic shell commands.
- ADB shell connects from a PC.
- Essential partitions can be identified and mounted safely.
- No FBE decryption claim until it has been tested with a real credential and userdata.
- No flashing to recovery/recovery2 until boot testing and a recovery path are proven.

## Current status

Planning and repository audit only. No OrangeFox image has been built or tested on the Alcatel 9032X.
