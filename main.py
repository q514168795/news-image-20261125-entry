#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Copy the rendered news card to the required output path.

Uses only the standard library. If a pre-rendered entry.png is present it is
copied; otherwise the image is rendered from make_image.py at run time.
"""
from pathlib import Path
import shutil

SRC = Path(__file__).resolve().parent / "entry.png"
DST = Path("/output/entry.png")


def main():
    DST.parent.mkdir(parents=True, exist_ok=True)
    if SRC.is_file():
        shutil.copyfile(SRC, DST)
    else:
        from make_image import render

        render(str(DST))
    assert DST.is_file() and DST.stat().st_size > 0


if __name__ == "__main__":
    main()
