# <div align="center">On GitHub, simply upload your recovery to compile a TWRP tailored to your device with one click!</div>

## Usage:
### 1. Fork this repository
### 2. Use tools like `bootimg` to unpack your recovery. Then, add `ro.product.first_api_level=(your Android SDK version)` at the bottom of `default.prop` or `prop.default`, and repackage it
### 3. Upload the repackaged `recovery.img` to this project, and copy the direct download link
### 4. Click on **Actions**, enter the direct link and TWRP version information
### 5. Click **Run**!
### 6. Once the build is complete, download the compiled Recovery from **Releases**
