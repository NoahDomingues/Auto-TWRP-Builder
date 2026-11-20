import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.create_vietnamese import create_locale


class VietnameseLocaleTests(unittest.TestCase):
    def make_source(self, root):
        source = root / "gui/theme/common/languages/en.xml"
        source.parent.mkdir(parents=True)
        source.write_text(
            """<?xml version="1.0" encoding="utf-8"?>
<language>
    <author>OrangeFox</author>
    <display>English</display>
    <resources>
        <string name="install">Install</string>
        <string name="wipe">Wipe</string>
        <string name="backups">Backups</string>
        <string name="restore">Restore</string>
        <string name="mount">Mount &amp; MTP</string>
        <string name="advanced">Advanced</string>
        <string name="reboot">Reboot</string>
        <string name="language">Language</string>
        <string name="terminal">Terminal</string>
        <string name="system">System</string>
        <string name="boot">Boot</string>
        <string name="recovery">Recovery</string>
        <string name="cache">Cache</string>
        <string name="data">Data</string>
        <string name="internal_storage">Internal Storage</string>
        <string name="micro_sdcard">Micro SDCard</string>
        <string name="usb_storage">USB-Storage</string>
        <string name="files">Files</string>
        <string name="copy_log">Copy Log to SD</string>
        <string name="install_zip">Install ZIP</string>
        <string name="install_image">Install Image</string>
        <string name="select_file">Select File</string>
        <string name="adb_sideload">ADB &amp; Sideload</string>
        <string name="select_storage">Select Storage</string>
        <string name="queue">Queue</string>
        <string name="clear_queue">Clear Queue</string>
        <string name="view_queue">View Queue</string>
        <string name="folder">Folder</string>
        <string name="file">File</string>
        <string name="working">Working...</string>
        <string name="failed">Failed</string>
        <string name="successful">Successful</string>
        <string name="wipe_caches">Wipe Caches</string>
        <string name="reboot_system">Reboot System</string>
        <string name="reboot_recovery">Reboot Recovery</string>
        <string name="power_off">Power Off</string>
        <string name="factory_reset">Factory Reset</string>
        <string name="advanced_wipe">Advanced Wipe</string>
        <string name="format_data">Format Data</string>
        <string name="partition_info">Partition Info</string>
        <string name="mount_label">Mount</string>
        <string name="settings">Settings</string>
        <string name="general">General</string>
        <string name="time_zone">Time Zone</string>
        <string name="screen_settings">Screen Settings</string>
        <string name="example">Untranslated example</string>
    </resources>
</language>
""",
            encoding="utf-8",
        )
        return source

    def test_generates_complete_vietnamese_xml_and_keeps_fallbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            target = create_locale(root)
            self.assertEqual(
                target.relative_to(root).as_posix(),
                "gui/theme/extra-languages/languages/vn.xml",
            )
            tree = ET.parse(target).getroot()
            self.assertEqual(tree.findtext("display"), "Vietnamese")
            values = {item.attrib["name"]: item.text for item in tree.findall("./resources/string")}
            self.assertEqual(values["install"], "Cài đặt")
            self.assertEqual(values["wipe"], "Xóa dữ liệu")
            self.assertEqual(values["example"], "Untranslated example")

    def test_fails_when_upstream_keys_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            text = source.read_text(encoding="utf-8")
            source.write_text(text.replace(">Install<", ">Install now<"), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "required labels"):
                create_locale(root)


if __name__ == "__main__":
    unittest.main()
