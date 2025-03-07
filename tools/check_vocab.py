"""Tool to check vocab list file for correctness."""

import argparse
import pathlib

from gaku import gaku_manager

RESOURCES = pathlib.Path(__file__).parent.parent / "resources"
WORKDIR = pathlib.Path(__file__).parent.parent / "userdata"

parser = argparse.ArgumentParser(description="Tool to check vocabulary list file")
parser.add_argument(
    "vocab_path",
    help="Path to vocabulary list file to check",
)


def check_vocab(vocab_path: str) -> None:
    """Runs the vocab list checks."""

    manager = gaku_manager.GakuManager(resource_dir=RESOURCES, workdir=WORKDIR)

    vocab_list = pathlib.Path(vocab_path)
    if not vocab_list.exists():
        print(f"Vocab list file not found: {vocab_list}")

    else:
        with open(vocab_list, "r", encoding="utf-8") as f:
            vocab = f.readlines()

        imports = manager.generate_vocab_import(vocab)
        print(f"Got {len(imports.generated_cards)} cards for the provide list")
        if len(imports.errors) == 0:
            print("There were no import notes, all OK")
        else:
            print("There were following notes from check:")
            print("\n".join(imports.errors))


if __name__ == "__main__":
    args = parser.parse_args()
    check_vocab(args.vocab_path)
