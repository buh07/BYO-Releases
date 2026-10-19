"""Run the exact release README command on a fresh native Actions runner."""

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

TAG = os.environ["RELEASE_TAG"]
TARGET = os.environ["EXPECTED_TARGET"]
LABELS = {
    "macos-aarch64": "macOS - Apple silicon",
    "macos-x86_64": "macOS - Intel",
    "windows-x86_64": "Windows - x86-64 (PowerShell)",
    "linux-x86_64": "Linux - x86-64, glibc 2.28+",
}
EVIDENCE = Path("install-evidence")
EVIDENCE.mkdir()
RESULT = {
    "tag": TAG,
    "target": TARGET,
    "steps": [],
    "errors": [],
    "doctor_analysis_ready": False,
    "status_analysis_ready": False,
}
LAUNCHER = (
    Path(os.environ["LOCALAPPDATA"]) / "BYO/bin/byo.exe"
    if os.name == "nt"
    else Path.home() / ".local/bin/byo"
)


def run(name, args, timeout=300):
    print(f"Running {name}", flush=True)
    stdout_path = EVIDENCE / f"{name}.stdout.txt"
    stderr_path = EVIDENCE / f"{name}.stderr.txt"
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            completed = subprocess.run(args, stdout=stdout, stderr=stderr, timeout=timeout)
    except subprocess.TimeoutExpired:
        RESULT["steps"].append({"name": name, "argv": args, "exit_code": None, "timeout_seconds": timeout})
        raise
    output = stdout_path.read_bytes().decode("utf-8", errors="replace")
    diagnostic = stderr_path.read_bytes().decode("utf-8", errors="replace")
    RESULT["steps"].append({"name": name, "argv": args, "exit_code": completed.returncode})
    print(output, end="")
    print(diagnostic, end="", file=sys.stderr)
    if completed.returncode:
        raise RuntimeError(f"{name} exited {completed.returncode}")
    return output


def main():
    # Refuse an unexpected pre-existing install before any cleanup can run.
    if LAUNCHER.exists():
        raise RuntimeError(f"Runner already has BYO installed at {LAUNCHER}")
    try:
        assert re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", TAG)
        base = f"https://github.com/buh07/BYO-Releases/releases/download/{TAG}"
        with urllib.request.urlopen(base + "/release-index.json", timeout=60) as response:
            index = json.load(response)
        assert index["tag"] == TAG and index["version"] == TAG[1:]
        records = [entry for entry in index["targets"] if entry["target"] == TARGET]
        assert len(records) == 1
        readme = subprocess.check_output(
            ["git", "show", TAG + ":README.md"], encoding="utf-8"
        )
        expression = rf"### {re.escape(LABELS[TARGET])}\n\n```(?:sh|powershell)\n([^\n]+)\n```"
        commands = re.findall(expression, readme)
        assert len(commands) == 1
        command = commands[0]
        assert base in command and records[0]["sha256"] in command
        assert "\n" not in command
        RESULT["command"] = command
        (EVIDENCE / "command.txt").write_text(command + "\n", encoding="utf-8")
        args = (
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command]
            if os.name == "nt"
            else ["sh", "-c", command]
        )
        run("one-line-install", args)
        checks = [
            ("version", [str(LAUNCHER), "--version"]),
            ("global-doctor", [str(LAUNCHER), "doctor", "--global"]),
            ("global-doctor-json", [str(LAUNCHER), "doctor", "--global", "--json"]),
            ("status", [str(LAUNCHER), "status"]),
        ]
        # Capture the whole independent post-install batch before reporting errors.
        for name, arguments in checks:
            try:
                output = run(name, arguments)
                if name == "version":
                    assert output.strip().endswith(index["version"]), output
                elif name == "global-doctor-json":
                    doctor = json.loads(output)
                    by_id = {item["id"]: item for item in doctor["checks"]}
                    for check_id in (
                        "runtime.manifest.integrity",
                        "runtime.sidecar.self-test",
                        "runtime.analysis.cppcheck",
                        "runtime.analysis.clangd",
                    ):
                        assert by_id.get(check_id, {}).get("status") == "passed", doctor
                    RESULT["doctor_analysis_ready"] = True
                elif name == "status":
                    status = json.loads(output)
                    assert status["runtime_version"] == index["version"], status
                    assert status["analysis"]["status"] == "ready", status
                    RESULT["status_analysis_ready"] = True
            except Exception as error:
                RESULT["errors"].append(f"{name}: {type(error).__name__}: {error}")
    except Exception as error:
        RESULT["errors"].append(f"{type(error).__name__}: {error}")
    finally:
        if LAUNCHER.exists():
            try:
                run("uninstall", [str(LAUNCHER), "uninstall", "--global"])
            except Exception as error:
                RESULT["errors"].append(f"Cleanup: {type(error).__name__}: {error}")
        RESULT["passed"] = not RESULT["errors"]
        (EVIDENCE / "result.json").write_text(json.dumps(RESULT, indent=2) + "\n", encoding="utf-8")
    if RESULT["errors"]:
        raise RuntimeError("; ".join(RESULT["errors"]))


if __name__ == "__main__":
    main()
