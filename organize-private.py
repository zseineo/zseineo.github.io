"""
organize-private.py
掃描 Private 根目錄的 HTML 檔案（符合「作品名稱_數字」格式），
在 Private 內（含子資料夾）尋找同名資料夾並移入；
若找不到，則在根目錄新建同名資料夾再移入。
"""

import re
import shutil
from pathlib import Path

PRIVATE_DIR = Path(__file__).parent / "Private"

# 比對「作品名稱_數字.html」，只處理 HTML 檔案
PATTERN = re.compile(r"^(.+)_(\d+)\.html$", re.IGNORECASE)


def find_existing_dir(name: str) -> Path | None:
    """在 Private 內（含子資料夾）遞迴尋找名稱符合的資料夾，回傳第一個找到的路徑。"""
    for d in PRIVATE_DIR.rglob(name):
        if d.is_dir():
            return d
    return None


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
        dest_dir = find_existing_dir(work_name) or PRIVATE_DIR / work_name
        dest_dir.mkdir(exist_ok=True)

        dest = dest_dir / file.name
        if dest.exists():
            print(f"[跳過] 目標已存在：{dest.relative_to(PRIVATE_DIR.parent)}")
            skipped += 1
            continue

        shutil.move(str(file), str(dest))
        print(f"[移動] {file.name}  →  {dest_dir.relative_to(PRIVATE_DIR.parent)}/")
        moved += 1

    print(f"\n完成：移動 {moved} 個，跳過 {skipped} 個。")


if __name__ == "__main__":
    organize()
