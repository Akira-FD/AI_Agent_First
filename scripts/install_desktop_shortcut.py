from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_desktop.py"
HIDDEN_LAUNCHER_PATH = ROOT / "scripts" / "run_desktop_hidden.vbs"


@dataclass
class ShortcutSpec:
    shortcut_path: Path
    target_path: Path
    arguments: str
    working_directory: Path
    icon_location: str
    description: str


def resolve_pythonw(executable: Path | None = None) -> Path:
    candidate = Path(executable or sys.executable).resolve()
    if candidate.name.lower() == "pythonw.exe":
        return candidate
    if candidate.name.lower() == "python.exe":
        sibling = candidate.with_name("pythonw.exe")
        if sibling.exists():
            return sibling
    return candidate


def render_hidden_launcher(python_executable: Path, script_path: Path, working_directory: Path) -> str:
    command = f'"{python_executable}" "{script_path}"'
    return (
        'Set shell = CreateObject("WScript.Shell")\n'
        f'shell.CurrentDirectory = "{working_directory}"\n'
        f'shell.Run "{command.replace(chr(34), chr(34) * 2)}", 0\n'
        "Set shell = Nothing\n"
    )


def ensure_hidden_launcher(
    launcher_path: Path = HIDDEN_LAUNCHER_PATH,
    *,
    python_executable: Path | None = None,
    script_path: Path = SCRIPT_PATH,
    working_directory: Path = ROOT,
) -> Path:
    launcher_text = render_hidden_launcher(
        resolve_pythonw(python_executable),
        script_path.resolve(),
        working_directory.resolve(),
    )
    launcher_path.write_text(launcher_text, encoding="utf-8")
    return launcher_path


def build_shortcut_spec(
    *,
    desktop_dir: Path,
    shortcut_name: str = "AI Agent First Client",
    launcher_path: Path = HIDDEN_LAUNCHER_PATH,
    python_executable: Path | None = None,
) -> ShortcutSpec:
    pythonw_path = resolve_pythonw(python_executable)
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    wscript_path = system_root / "System32" / "wscript.exe"
    return ShortcutSpec(
        shortcut_path=desktop_dir / f"{shortcut_name}.lnk",
        target_path=wscript_path,
        arguments=f'"{launcher_path.resolve()}"',
        working_directory=ROOT,
        icon_location=f"{pythonw_path},0",
        description="AI Agent First desktop client",
    )


def create_windows_shortcut(spec: ShortcutSpec) -> Path:
    def _ps(value: str) -> str:
        return value.replace("'", "''")

    command = "\n".join(
        [
            "$shell = New-Object -ComObject WScript.Shell",
            f"$shortcut = $shell.CreateShortcut('{_ps(str(spec.shortcut_path))}')",
            f"$shortcut.TargetPath = '{_ps(str(spec.target_path))}'",
            f"$shortcut.Arguments = '{_ps(spec.arguments)}'",
            f"$shortcut.WorkingDirectory = '{_ps(str(spec.working_directory))}'",
            f"$shortcut.IconLocation = '{_ps(spec.icon_location)}'",
            f"$shortcut.Description = '{_ps(spec.description)}'",
            "$shortcut.Save()",
        ]
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=True,
    )
    return spec.shortcut_path


def install_shortcut(shortcut_name: str = "AI Agent First Client") -> Path:
    desktop_dir = Path.home() / "Desktop"
    launcher_path = ensure_hidden_launcher()
    spec = build_shortcut_spec(
        desktop_dir=desktop_dir,
        shortcut_name=shortcut_name,
        launcher_path=launcher_path,
    )
    return create_windows_shortcut(spec)


def main() -> None:
    installed = install_shortcut()
    print(installed)


if __name__ == "__main__":
    main()
