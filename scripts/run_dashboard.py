from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app" / "streamlit_app.py"


def main() -> int:
    command = [sys.executable, "-m", "streamlit", "run", str(APP_PATH)]
    print("Running dashboard:")
    print(" ".join(command))
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
