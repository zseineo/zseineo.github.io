"""
organize-private.py
將 Private 資料夾內符合「作品名稱_數字」格式的檔案，
移入與作品名稱同名的子資料夾（不存在則自動建立）。
"""

import re
import shutil
from pathlib import Path

PRIVATE_DIR = Path(__file__).parent / "Private"

# 比對「作品名稱_數字」，數字部分允許多位數，副檔名任意
PATTERN = re.compile(r"^(.+)_(\d+)(\..+)?$")


def organize():
    if not PRIVATE_DIR.is_dir():
        print(f"找不到資料夾：{PRIVATE_DIR}")
        return

    moved = 0
    skipped = 0

    for file in sorted(PRIVATE_DIR.iterdir()):
        if not file.is_file():
            continue

        m = PATTERN.match(file.name)
        if not m:
            skipped += 1
            continue

        work_name = m.group(1)
        dest_dir = PRIVATE_DIR / work_name

        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / file.name

        if dest.exists():
            print(f"[跳過] 目標已存在：{dest.relative_to(PRIVATE_DIR.parent)}")
            skipped += 1
            continue

        shutil.move(str(file), str(dest))
        print(f"[移動] {file.name}  →  {work_name}/")
        moved += 1

    print(f"\n完成：移動 {moved} 個，跳過 {skipped} 個。")


if __name__ == "__main__":
    organize()
