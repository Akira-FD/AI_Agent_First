import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.install_desktop_shortcut as install_desktop_shortcut


class InstallDesktopShortcutTests(unittest.TestCase):
    def test_render_hidden_launcher_uses_hidden_run_mode(self) -> None:
        launcher = install_desktop_shortcut.render_hidden_launcher(
            Path(r"C:\Python\pythonw.exe"),
            Path(r"C:\repo\scripts\run_desktop.py"),
            Path(r"C:\repo"),
        )

        self.assertIn('shell.Run', launcher)
        self.assertIn(', 0', launcher)
        self.assertIn('pythonw.exe', launcher)
        self.assertIn('run_desktop.py', launcher)

    def test_ensure_hidden_launcher_writes_launcher_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = Path(tmpdir) / "run_desktop_hidden.vbs"
            result = install_desktop_shortcut.ensure_hidden_launcher(
                launcher_path,
                python_executable=Path(r"C:\Python\pythonw.exe"),
                script_path=Path(r"C:\repo\scripts\run_desktop.py"),
                working_directory=Path(r"C:\repo"),
            )

            self.assertEqual(result, launcher_path)
            self.assertTrue(launcher_path.exists())
            self.assertIn("CurrentDirectory", launcher_path.read_text(encoding="utf-8"))

    def test_build_shortcut_spec_targets_wscript_and_desktop_shortcut(self) -> None:
        with patch.dict("os.environ", {"SystemRoot": r"C:\Windows"}, clear=False):
            spec = install_desktop_shortcut.build_shortcut_spec(
                desktop_dir=Path(r"C:\Users\JXW\Desktop"),
                shortcut_name="AI Agent First Client",
                launcher_path=Path(r"C:\repo\scripts\run_desktop_hidden.vbs"),
                python_executable=Path(r"C:\Python\python.exe"),
            )

        self.assertEqual(spec.shortcut_path, Path(r"C:\Users\JXW\Desktop\AI Agent First Client.lnk"))
        self.assertEqual(spec.target_path, Path(r"C:\Windows\System32\wscript.exe"))
        self.assertIn("run_desktop_hidden.vbs", spec.arguments)
        self.assertIn("python", spec.icon_location.lower())

    def test_install_shortcut_creates_launcher_and_shortcut(self) -> None:
        with (
            patch.object(install_desktop_shortcut, "ensure_hidden_launcher", return_value=Path(r"C:\repo\scripts\run_desktop_hidden.vbs")) as ensure_launcher,
            patch.object(install_desktop_shortcut, "create_windows_shortcut", return_value=Path(r"C:\Users\JXW\Desktop\AI Agent First Client.lnk")) as create_shortcut,
            patch("pathlib.Path.home", return_value=Path(r"C:\Users\JXW")),
        ):
            shortcut_path = install_desktop_shortcut.install_shortcut()

        ensure_launcher.assert_called_once()
        create_shortcut.assert_called_once()
        self.assertEqual(shortcut_path, Path(r"C:\Users\JXW\Desktop\AI Agent First Client.lnk"))


if __name__ == "__main__":
    unittest.main()
