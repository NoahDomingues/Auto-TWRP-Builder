# Alcatel 9032X TWRP bring-up

Target device: Alcatel 9032X / Apollo_8_4G

Known device facts:
- SoC: MediaTek MT6761
- Android: 10 / SDK 29
- First API level: 29
- Userspace architecture: ARM32 (armeabi-v7a)
- Recovery partition size: 33,554,432 bytes (32 MiB)
- Input image: stock `recovery-original.img` from the GitHub Release tagged `Recovery`

## Current status

This repository currently performs a **device-tree preflight only**. It does not compile or flash TWRP.

The workflow downloads the stock recovery image, verifies its SHA-256 and exact size, runs `twrpdtgen`, and uploads the generated device tree as a GitHub Actions artifact.

## Run the preflight

1. Open the Actions tab.
2. Select **TWRP Device Tree Preflight**.
3. Choose **Run workflow** on branch `master`.
4. Keep the default image URL and SHA-256.
5. Start the workflow.
6. When it finishes, download the artifact named `alcatel-9032x-device-tree-preflight`.

## Important safety notes

- Do not flash a recovery built for another device.
- Do not assume an MT6761 donor tree is compatible; some MT6761 devices use ARM64 while this tablet uses ARM32.
- Do not start a full TWRP compile until the generated tree, kernel architecture, fstab, partition layout, encryption support, and recovery init configuration have been reviewed.
- No workflow in this repository flashes the tablet.
