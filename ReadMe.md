# Auto TWRP Builder

A one-click automated TWRP compiler for Android devices. 🔧

[<img src="https://github.com/user-attachments/assets/0a4bb969-dec8-42f2-afd8-0858283ac3fe">](https://discord.gg/3zbfaTNN7V)

## 💡 Usage

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

## 🧪 Built For

This tool is designed for Android modders and device maintainers who want a simplified and automated way to generate recovery builds. Whether you're personalizing your device or contributing to the community, this tool should give you a head start.

##  ⚡ Contribute

Have feedback or ideas?  Head over to the **[Issues section](https://github.com/NoahDomingues/Auto-TWRP-Builder/issues)** or open a **[pull request](https://github.com/NoahDomingues/Auto-TWRP-Builder/pulls)** to improve the tool.

## 🤝 Support

If you run into any issues, check out our **[Discord server](https://discord.gg/3zbfaTNN7V)** or open a GitHub issue to let us know!

[<img src="https://github.com/user-attachments/assets/f61046f5-1dc5-4b0c-87f8-4a94d6cbac96">](https://discord.gg/3zbfaTNN7V)

**⭐ If this tool was of any use to you, please consider giving it a Star - it would make my day! ⭐**

Thanks to **[ColdWindScholar](https://github.com/ColdWindScholar)** for building the [initial project](https://github.com/ColdWindScholar/Auto-Twrp-Builder) from which this was forked.

[<img src="https://img.shields.io/badge/GitHub-Actions-blue?style=for-the-badge&logo=github-actions&logoColor=white">](https://github.com/NoahDomingues/Auto-TWRP-Builder/actions) [<img src="https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white">](https://discord.gg/3zbfaTNN7V)


<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" />
</div>
