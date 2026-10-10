import importlib.util
import json
import os
import plistlib
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module("workbuddy_checkin", ROOT / "scripts" / "workbuddy_checkin.py")
installer = load_module("workbuddy_installer", ROOT / "scripts" / "install.py")


class CoreTests(unittest.TestCase):
    def test_windows_prefers_localappdata_and_supports_auth_case(self):
        env = {"LOCALAPPDATA": r"C:\Users\Test User\AppData\Local", "APPDATA": r"C:\Users\Test User\AppData\Roaming"}
        paths = core.candidate_token_files("win32", env, Path(r"C:\Users\Test User"))
        self.assertTrue(str(paths[0]).startswith(env["LOCALAPPDATA"]))
        self.assertTrue(any(path.parent.name.lower() == "auth" for path in paths))
        self.assertTrue(any(str(path).startswith(env["APPDATA"]) for path in paths))

    def test_macos_token_load_and_dry_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbuddy-desktop.info"
            path.write_text(json.dumps({"auth": {"accessToken": "x" * 40}}), encoding="utf-8")
            self.assertEqual(core.load_token(path), "x" * 40)

    def test_invalid_token_is_rejected_without_echo(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbuddy-desktop.info"
            path.write_text(json.dumps({"auth": {"accessToken": "secret"}}), encoding="utf-8")
            with self.assertRaises(RuntimeError) as error:
                core.load_token(path)
            self.assertNotIn("secret", str(error.exception))

    def test_idempotent_messages(self):
        self.assertTrue(core.is_idempotent_message("今天已签到，请明天再来"))
        self.assertTrue(core.is_idempotent_message("请求处理中，请勿重复操作"))
        self.assertFalse(core.is_idempotent_message("登录失败"))

    def test_single_instance_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / "checkin.lock"
            with core.single_instance(lock):
                with self.assertRaises(RuntimeError):
                    with core.single_instance(lock):
                        pass
            self.assertFalse(lock.exists())


class InstallerTests(unittest.TestCase):
    def test_time_validation(self):
        self.assertEqual(installer.parse_time("06:05"), (6, 5))
        with self.assertRaises(Exception):
            installer.parse_time("25:00")

    def test_macos_plist_roundtrip(self):
        value = installer.build_macos_plist(
            Path("/usr/bin/python3"),
            Path("/Users/Test User/Library/Application Support/WorkBuddyAutoCheckin/workbuddy_checkin.py"),
            Path("/Users/Test User/Library/Logs/WorkBuddyAutoCheckin/checkin.log"),
            6,
            5,
        )
        data = plistlib.loads(plistlib.dumps(value))
        self.assertEqual(data["Label"], installer.LABEL)
        self.assertEqual(data["StartCalendarInterval"], {"Hour": 6, "Minute": 5})
        self.assertIn("Test User", data["ProgramArguments"][1])

    def test_generic_legacy_job_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            launch_agents = Path(folder)
            legacy = {
                "Label": "com.example.workbuddy.checkin",
                "ProgramArguments": ["/usr/bin/python3", "/Users/example/checkin.py"],
            }
            unrelated = {"Label": "com.example.backup", "ProgramArguments": ["/bin/true"]}
            with (launch_agents / "legacy.plist").open("wb") as handle:
                plistlib.dump(legacy, handle)
            with (launch_agents / "unrelated.plist").open("wb") as handle:
                plistlib.dump(unrelated, handle)
            jobs = installer.find_mac_legacy_jobs(launch_agents)
            self.assertEqual([(label, path.name) for label, path in jobs], [("com.example.workbuddy.checkin", "legacy.plist")])

    def test_windows_xml_roundtrip_and_quoting(self):
        xml = installer.build_windows_task_xml(
            Path(r"C:\Program Files\Python\python.exe"),
            Path(r"C:\Users\Test User\AppData\Local\WorkBuddyAutoCheckin\workbuddy_checkin.py"),
            Path(r"C:\Users\Test User\AppData\Local\WorkBuddyAutoCheckin\logs\checkin.log"),
            6,
            5,
            r"DESKTOP\Test User",
        )
        root = ET.fromstring(xml)
        ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
        self.assertEqual(root.findtext(".//t:LogonType", namespaces=ns), "InteractiveToken")
        self.assertEqual(root.findtext(".//t:StartWhenAvailable", namespaces=ns), "true")
        arguments = root.findtext(".//t:Arguments", namespaces=ns)
        self.assertIn('"C:\\Users\\Test User', arguments)

    def test_platform_dry_runs(self):
        self.assertEqual(installer.main(["--platform", "macos", "--dry-run", "--time", "07:30"]), 0)
        self.assertEqual(installer.main(["--platform", "windows", "--dry-run", "--time", "07:30"]), 0)


class ParseResponseTests(unittest.TestCase):
    def test_parse_response_returns_utf8_json_object(self):
        response = core.parse_response('{"message":"签到成功","count":0}'.encode("utf-8"))
        self.assertEqual(response, {"message": "签到成功", "count": 0})

    def test_parse_response_rejects_malformed_json(self):
        with self.assertRaisesRegex(RuntimeError, "服务返回了无法识别的数据"):
            core.parse_response(b'{"message":')

    def test_parse_response_rejects_valid_non_object_json_values(self):
        for raw in (b"null", b"[]", b'"ok"', b"0"):
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(RuntimeError, "服务返回格式不兼容"):
                    core.parse_response(raw)


if __name__ == "__main__":
    unittest.main()
