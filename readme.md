# Auto TWRP Builder

A one-click TWRP compiler for your device—just upload your recovery on GitHub and let the automation do the rest! 🔧

[<img src="https://github.com/user-attachments/assets/0a4bb969-dec8-42f2-afd8-0858283ac3fe">](https://github.com/NoahDomingues/Auto-TWRP-Builder)

## 📥 How to Use

Follow these steps to generate your own TWRP build:

- **Step 1**: Fork this repository to your GitHub account.
- **Step 2**: Use a tool like `bootimg` to unpack your `recovery.img`.  
  Edit `default.prop` or `prop.default` by appending this line at the bottom:  
  `ro.product.first_api_level=(your Android SDK version)`  
  Then repack the recovery.
- **Step 3**: Upload the repacked `recovery.img` to your forked repo and copy its direct link.
- **Step 4**: Go to the **Actions** tab in your repo, and start a new workflow run.  
  Paste the direct link and specify the desired TWRP version.
- **Step 5**: Hit **Run workflow** and let the system build your TWRP image.
- **Step 6**: After the build finishes, download the compiled TWRP recovery from the **Releases** section.

![Example Workflow Screenshot](https://github.com/user-attachments/assets/placeholder-screenshot)

## 🧪 Built For

This tool is designed for Android modders and device maintainers who want a simplified and automated way to generate recovery builds. Whether you're personalizing your device or contributing to the community, this project gives you a head start.

## 🤝 Contribute & Collaborate

Have feedback or ideas?  
Head over to the [Issues](https://github.com/ColdWindScholar/Auto-Twrp-Builder/issues) or open a PR to improve the tool.

**⭐ If this tool was of any use to you, please consider giving it a Star - it would make my day! ⭐**

[<img src="https://img.shields.io/badge/GitHub-Actions-blue?style=for-the-badge&logo=github-actions&logoColor=white">](https://github.com/ColdWindScholar/Auto-Twrp-Builder/actions)

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" />
</div>
