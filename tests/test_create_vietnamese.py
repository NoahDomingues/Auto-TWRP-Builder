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
