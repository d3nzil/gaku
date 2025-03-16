"""Script to build gaku package using pyinstaller."""

import os
import datetime
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DIST_DIR = REPO_ROOT / "dist"


def build_frontend() -> None:
    """Builds Gaku frontend."""
    command: list[str] = ["npm", "run", "build"]
    subprocess.run(command, cwd=REPO_ROOT / "gaku-frontend", shell=True, check=True)


def build_docs() -> None:
    """Builds the user documentation."""
    command: list[str] = ["mkdocs", "build"]
    subprocess.run(command, cwd=REPO_ROOT / "docs-user", check=True)


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
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def copy_vocab() -> None:
    """Copies the vocabulary data to pyinstaller Gaku build."""
    dest_dir = REPO_ROOT / "dist" / "gaku"
    shutil.copytree(src=REPO_ROOT / "vocab-text", dst=dest_dir / "vocab-text")


def package_build() -> None:
    """Creates platform appropriate package."""

    version = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    base_name = "gaku"
    if sys.platform == "win32":
        pkg_name = f"{base_name}_windows.zip"

        command: list[str] = [
            "python",
            "-m",
            "zipfile",
            "--create",
            str(pkg_name),
            "./gaku",
        ]

    elif sys.platform == "linux":
        pkg_name = f"{base_name}_linux.tgz"
        command: list[str] = [
            "tar",
            "-czf",
            pkg_name,
            "--owner",
            "0",
            "--group",
            "0",
            "./gaku",
        ]
    else:
        print("Unsupported platform, skipping creating package archive")
        return

    subprocess.run(command, cwd=DIST_DIR, check=True)
    pkg = Path(DIST_DIR) / pkg_name
    pkg.rename(DIST_DIR / f"{base_name}_{version}{pkg.suffix}")


def copy_license() -> None:
    """Copies license file to the build directory."""
    shutil.copy(REPO_ROOT / "LICENSE.md", dst=DIST_DIR)


if __name__ == "__main__":
    # pre-build steps
    build_frontend()
    build_docs()
    # package build
    build_pyinstaller()
    # post build steps
    copy_vocab()
    copy_license()
    package_build()
