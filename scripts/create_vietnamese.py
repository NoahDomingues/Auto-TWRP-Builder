#!/usr/bin/env python3

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path("gui/theme/common/languages/en.xml")
TARGET = Path("gui/theme/extra-languages/languages/vn.xml")

TRANSLATIONS = {
    "System": "Hệ thống",
    "System Image": "Ảnh hệ thống",
    "Boot": "Khởi động",
    "Recovery": "Recovery",
    "Cache": "Bộ nhớ đệm",
    "Data": "Dữ liệu",
    "Internal Storage": "Bộ nhớ trong",
    "Micro SDCard": "Thẻ microSD",
    "USB-Storage": "Bộ nhớ USB",
    "Install": "Cài đặt",
    "Wipe": "Xóa dữ liệu",
    "Backups": "Sao lưu",
    "Restore": "Khôi phục",
    "Mount & MTP": "Gắn phân vùng & MTP",
    "Files": "Tệp",
    "Advanced": "Nâng cao",
    "Reboot": "Khởi động lại",
    "Copy Log to SD": "Sao chép nhật ký vào thẻ SD",
    "Install ZIP": "Cài đặt ZIP",
    "Install Image": "Cài đặt ảnh",
    "Install IMAGE": "Cài đặt ảnh",
    "Select File": "Chọn tệp",
    "ADB & Sideload": "ADB và Sideload",
    "Select Storage": "Chọn bộ nhớ",
    "Queue": "Hàng đợi",
    "Clear Queue": "Xóa hàng đợi",
    "View Queue": "Xem hàng đợi",
    "Folder": "Thư mục",
    "File": "Tệp",
    "Working...": "Đang xử lý...",
    "Failed": "Thất bại",
    "Successful": "Thành công",
    "Wipe Caches": "Xóa bộ nhớ đệm",
    "Reboot System": "Khởi động lại hệ thống",
    "Reboot Recovery": "Khởi động lại Recovery",
    "Power Off": "Tắt nguồn",
    "Factory Reset": "Khôi phục cài đặt gốc",
    "Advanced Wipe": "Xóa nâng cao",
    "Wipe Encryption from Data": "Xóa mã hóa khỏi Data",
    "Formatting Data...": "Đang định dạng Data...",
    "Format Data": "Định dạng Data",
    "Partition Info": "Thông tin phân vùng",
    "Partition Options": "Tùy chọn phân vùng",
    "Mount Point": "Điểm gắn kết",
    "File system": "Hệ thống tệp",
    "Present": "Tồn tại",
    "Removable": "Có thể tháo rời",
    "Size": "Dung lượng",
    "Used": "Đã dùng",
    "Free": "Còn trống",
    "Backup Size": "Kích thước bản sao lưu",
    "Backup completed": "Sao lưu hoàn tất",
    "Restore completed": "Khôi phục hoàn tất",
    "Mount": "Gắn phân vùng",
    "Mount system partitions read-only": "Gắn phân vùng hệ thống ở chế độ chỉ đọc",
    "Decrypt Data": "Giải mã Data",
    "Disable MTP": "Tắt MTP",
    "Enable MTP": "Bật MTP",
    "USB Storage": "Bộ nhớ USB",
    "Settings": "Cài đặt",
    "General": "Chung",
    "Use 24-hour clock": "Sử dụng định dạng 24 giờ",
    "Time Zone": "Múi giờ",
    "Screen Settings": "Cài đặt màn hình",
    "Timeout": "Thời gian chờ",
    "Rotation": "Xoay màn hình",
    "Brightness": "Độ sáng",
    "Vibration": "Rung",
    "Button Vibration": "Rung nút",
    "Keyboard Vibration": "Rung bàn phím",
    "Action Vibration": "Rung thao tác",
    "Language": "Ngôn ngữ",
    "Terminal": "Terminal",
    "Copy Log to SD Card": "Sao chép nhật ký vào thẻ SD",
    "Actions": "Thao tác",
    "Select a File or Folder": "Chọn tệp hoặc thư mục",
    "Copy": "Sao chép",
    "Move": "Di chuyển",
    "Delete": "Xóa",
    "Rename": "Đổi tên",
    "Set Permissions": "Đặt quyền truy cập",
    "Permissions": "Quyền truy cập",
    "Decrypt": "Giải mã",
    "Data Partition": "Phân vùng Data",
    "Data Partition is encrypted": "Phân vùng Data đã được mã hóa",
    "Enter password": "Nhập mật khẩu",
    "Pattern failed!": "Sai hình mở khóa!",
    "Please try again.": "Vui lòng thử lại.",
    "Trying Decryption": "Đang thử giải mã",
    "ADB Sideload": "ADB Sideload",
    "Wipe Dalvik Cache": "Xóa Dalvik Cache",
    "Wipe Cache": "Xóa Cache",
    "Swipe to Start Sideload": "Vuốt để bắt đầu Sideload",
    "Fix Contexts": "Sửa SELinux Contexts",
    "Fix SELinux contexts": "Sửa ngữ cảnh SELinux",
    "OK": "Đồng ý",
    "Cancel": "Hủy",
    "Install Recovery Ramdisk": "Cài đặt Recovery Ramdisk",
    "Install Kernel": "Cài đặt Kernel",
    "Back up existing image first": "Sao lưu ảnh hiện tại trước",
    "Installing...": "Đang cài đặt...",
    "Install Complete": "Cài đặt hoàn tất",
    "Decrypt Users": "Giải mã người dùng",
    "Selected user": "Người dùng đã chọn",
    "Users": "Người dùng",
    "No OS installed! Are you sure you wish to reboot?": "Chưa cài hệ điều hành! Bạn có chắc muốn khởi động lại không?",
    "No OS installed! Are you sure you wish to power off?": "Chưa cài hệ điều hành! Bạn có chắc muốn tắt nguồn không?",
    "Battery": "Pin",
    "Status bar": "Thanh trạng thái",
    "Display": "Hiển thị",
    "Regional": "Khu vực",
    "Customization": "Tùy chỉnh",
    "About": "Giới thiệu",
    "Version": "Phiên bản",
    "Quick Backup": "Sao lưu nhanh",
    "Show battery icon": "Hiện biểu tượng pin",
    "NavBar style": "Kiểu thanh điều hướng",
    "NavBar background": "Nền thanh điều hướng",
    "Favorite folders": "Thư mục yêu thích",
    "Please wait...": "Vui lòng chờ...",
}

REQUIRED_STRINGS = {
    "Install",
    "Wipe",
    "Backups",
    "Restore",
    "Mount & MTP",
    "Advanced",
    "Reboot",
    "Language",
    "Terminal",
}


def normalize(value):
    return re.sub(r"\s+", " ", value or "").strip()


def create_locale(source_root):
    source = source_root / SOURCE
    target = source_root / TARGET
    if not source.is_file():
        raise RuntimeError(f"Base English language file not found: {source}")

    try:
        tree = ET.parse(source)
    except ET.ParseError as error:
        raise RuntimeError(f"English language XML is invalid: {error}") from error

    root = tree.getroot()
    if root.tag != "language":
        raise RuntimeError(f"Unexpected language root element: {root.tag}")

    display = root.find("display")
    resources = root.find("resources")
    if display is None or resources is None:
        raise RuntimeError("English language file must contain display and resources elements")

    display.text = "Vietnamese"
    author = root.find("author")
    if author is not None:
        author.text = "GernalOS Lite Vietnamese Translation"

    replaced = set()
    for element in resources.findall("string"):
        english = normalize(element.text)
        translated = TRANSLATIONS.get(english)
        if translated is not None:
            element.text = translated
            replaced.add(english)

    missing = REQUIRED_STRINGS - replaced
    if missing:
        raise RuntimeError(
            "The upstream English file changed; required labels were not found: "
            + ", ".join(sorted(missing))
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="    ")
    tree.write(target, encoding="utf-8", xml_declaration=True)

    check = ET.parse(target).getroot()
    if check.findtext("display") != "Vietnamese":
        raise RuntimeError("Generated locale has an invalid display name")
    if len(replaced) < 35:
        raise RuntimeError(f"Only {len(replaced)} labels were translated; refusing an incomplete output")

    print(f"Generated locale: {target}")
    print(f"Translated labels: {len(replaced)}")
    print("Locale code: vn")
    print("Unmapped strings retain their English source text.")
    return target


def main():
    parser = argparse.ArgumentParser(
        description="Generate the GernalOS Vietnamese locale from the exact synced OrangeFox English resources"
    )
    parser.add_argument("--source", type=Path, required=True, help="OrangeFox source root")
    args = parser.parse_args()
    create_locale(args.source)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"Vietnamese locale generation failed: {error}")
