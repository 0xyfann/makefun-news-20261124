#!/usr/bin/env python3
"""make.fun news-image-20261124 entry runner.

Regenerates the deterministic 1024x1024 newspaper PNG (entry.png) with
draw_news.py, then copies it into $MAKEFUN_OUTPUT_DIR (or /output when the
variable is not set). Standard library only.
"""

import hashlib
import os
import shutil
import subprocess
import sys

ENTRY_NAME = "entry.png"
ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    draw_script = os.path.join(ROOT, "draw_news.py")
    entry_path = os.path.join(ROOT, ENTRY_NAME)

    # Reproduce the artwork deterministically first.
    subprocess.run([sys.executable, draw_script], check=True, cwd=ROOT)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, ENTRY_NAME)
    shutil.copyfile(entry_path, dest)

    src_bytes = open(entry_path, "rb").read()
    dst_bytes = open(dest, "rb").read()
    if src_bytes != dst_bytes:
        raise SystemExit("error: copied entry.png differs from the generated artwork")
    digest = hashlib.sha256(dst_bytes).hexdigest()
    size = len(dst_bytes)
    print("copied %s -> %s (%d bytes, sha256=%s)" % (entry_path, dest, size, digest))


if __name__ == "__main__":
    main()
