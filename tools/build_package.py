"""Script to build gaku package using pyinstaller."""

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def build_docs() -> None:
    """Builds the user documentation."""
    command: list[str] = ["mkdocs", "build"]
    subprocess.run(command, cwd=REPO_ROOT / "docs-user")


def build_pyinstaller() -> None:
    """Builds the pyinstaller package."""
    command: list[str] = [
        "pyinstaller",
        "--name",
        "gaku",
        "--add-data",
        "./resources:resources",
        "--add-data",
        "./alembic:alembic",
        "--add-data",
        "./alembic.ini:.",
        "--hidden-import",
        "alembic",
        "--exclude-module",
        "pillow",
        "--exclude-module",
        "PIL",
        "--additional-hooks-dir",
        ".",
        "main.py",
        "-i",
        "icon.png",
    ]
    subprocess.run(command, cwd=REPO_ROOT)


def copy_vocab() -> None:
    """Copies the vocabulary data to pyinstaller Gaku build."""
    dest_dir = REPO_ROOT / "dist" / "gaku"
    shutil.copytree(src=REPO_ROOT / "vocab-text", dst=dest_dir / "vocab-text")


if __name__ == "__main__":
    # pre-build steps
    build_docs()
    # package build
    build_pyinstaller()
    # post build steps
    copy_vocab()
