#!/usr/bin/env python3
"""
初始化新作品資料夾，生成 index.html 與 notice.txt，並自動寫入根首頁目錄。

用法：直接執行腳本，選擇 gallery/ 內的目標資料夾即可。
      若資料夾尚未存在，可先在 gallery/ 內新建再選取，或直接選取 gallery/ 並輸入名稱。
"""
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

SCRIPT_DIR = Path(__file__).parent
GALLERY_DIR = SCRIPT_DIR / "gallery"
ROOT_INDEX = SCRIPT_DIR / "index.html"
NOTICE_DEFAULT = "作者 "
RESERVED_NAMES = {"working"}


def natural_key(s):
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]


def build_index(folder: Path, title: str) -> str:
    files = sorted(
        [f.name for f in folder.glob("*.html") if f.name != "index.html"],
        key=natural_key,
    )
    links = "\n".join(f'    <li><a href="{f}">{f[:-5]}</a></li>' for f in files)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: sans-serif;
      max-width: 600px;
      margin: 40px auto;
      padding: 0 20px;
      background: #f9f9f9;
      color: #333;
    }}
    h1 {{ font-size: 1.5rem; margin-bottom: 24px; }}
    h2 {{ font-size: 1rem; margin-bottom: 10px; color: #555; }}
    .back {{
      display: inline-block;
      margin-bottom: 20px;
      font-size: 0.9rem;
      color: #888;
      text-decoration: none;
    }}
    .back:hover {{ text-decoration: underline; }}
    .notice {{
      background: #fff8e1;
      border-left: 3px solid #ffc107;
      padding: 12px 16px;
      margin-bottom: 28px;
      white-space: pre-wrap;
      font-size: 0.9rem;
      line-height: 1.6;
      border-radius: 0 4px 4px 0;
    }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 8px 0; }}
    a {{ text-decoration: none; color: #0066cc; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <a class="back" href="../../">← 返回首頁</a>
  <h1>{title}</h1>

  <h2>公告</h2>
  <div class="notice" id="notice">讀取中…</div>

  <div style="margin-bottom: 28px; display: flex; align-items: center; gap: 12px;">
    <label for="bg-color" style="font-size: 0.9rem; color: #555;">網頁底色</label>
    <input type="color" id="bg-color" value="#ffffff"
      style="width: 40px; height: 32px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; padding: 2px;">
    <button id="reset-color"
      style="font-size: 0.8rem; color: #888; background: none; border: 1px solid #ccc; border-radius: 4px; padding: 4px 10px; cursor: pointer;">
      重設
    </button>
  </div>

  <h2>作品列表</h2>
  <ul>
{links}
  </ul>

  <script>
    fetch('notice.txt?_=' + Date.now())
      .then(r => r.text())
      .then(t => {{
        document.getElementById('notice').textContent = t.trim() || '（無公告）';
      }})
      .catch(() => {{
        document.getElementById('notice').textContent = '（無法載入公告）';
      }});

    const picker = document.getElementById('bg-color');
    const resetBtn = document.getElementById('reset-color');
    const KEY = 'pagebgColor';

    const saved = localStorage.getItem(KEY);
    if (saved) {{
      document.body.style.backgroundColor = saved;
      picker.value = saved;
    }}

    picker.addEventListener('input', () => {{
      document.body.style.backgroundColor = picker.value;
      localStorage.setItem(KEY, picker.value);
    }});

    resetBtn.addEventListener('click', () => {{
      localStorage.removeItem(KEY);
      picker.value = '#ffffff';
      document.body.style.backgroundColor = '';
    }});
  </script>
</body>
</html>
"""


def get_japanese_name(folder: Path) -> str | None:
    """從資料夾內任一 HTML 檔名推導日文原名（去掉底線與末尾數字）。"""
    for f in sorted(folder.glob("*.html")):
        if f.name == "index.html":
            continue
        base = re.sub(r'_\d+$', '', f.stem)
        if base:
            return base
    return None


def update_root_index(name: str, display_text: str) -> bool:
    """在根首頁 <ul> 末端插入新作品連結，若已存在則跳過。回傳是否有寫入。"""
    if not ROOT_INDEX.exists():
        print(f"！找不到根首頁 {ROOT_INDEX}，跳過自動寫入")
        return False

    content = ROOT_INDEX.read_text(encoding="utf-8")
    href = f"gallery/{name}/"

    if href in content:
        print(f"根首頁已有 {name} 的連結，跳過")
        return False

    new_item = f'    <li><a href="{href}">{display_text}</a></li>'
    # 在 </ul> 前插入（只改第一個 </ul>，即作品列表那個）
    updated = re.sub(r'[ \t]*</ul>', f"{new_item}\n  </ul>", content, count=1)
    if updated == content:
        print("！找不到 </ul>，無法自動寫入根首頁")
        return False

    ROOT_INDEX.write_text(updated, encoding="utf-8")
    print(f"已在根首頁目錄加入：{display_text}")
    return True


def pick_folder() -> Path | None:
    """開啟資料夾選擇器，預設在 gallery/ 目錄，回傳選取的 Path 或 None（取消）。"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected = filedialog.askdirectory(
        title="選擇要初始化的作品資料夾（在 gallery/ 內選取或新建）",
        initialdir=str(GALLERY_DIR),
        mustexist=False,
    )
    root.destroy()
    return Path(selected) if selected else None


def main():
    folder = pick_folder()

    if folder is None:
        print("已取消。")
        sys.exit(0)

    # 確認選取的資料夾是 gallery/ 的直接子目錄
    try:
        rel = folder.relative_to(GALLERY_DIR)
    except ValueError:
        messagebox.showerror("錯誤", f"請在 gallery/ 目錄內選取資料夾。\n選取的路徑：{folder}")
        sys.exit(1)

    parts = rel.parts
    if len(parts) != 1:
        messagebox.showerror("錯誤", f"請直接選取 gallery/ 的子資料夾，不要選到更深的層級。\n選取：{folder}")
        sys.exit(1)

    name = parts[0]

    if name in RESERVED_NAMES:
        messagebox.showerror("錯誤", f"'{name}' 為保留名稱，不可作為作品名。")
        sys.exit(1)

    if not folder.exists():
        folder.mkdir(parents=True)
        print(f"已建立資料夾 {folder}")

    if not folder.is_dir():
        messagebox.showerror("錯誤", f"{folder} 不是資料夾。")
        sys.exit(1)

    title = name
    index_path = folder / "index.html"
    notice_path = folder / "notice.txt"

    index_path.write_text(build_index(folder, title), encoding="utf-8")
    print(f"已生成 {index_path}")

    notice_skipped = False
    if notice_path.exists():
        print(f"已存在 {notice_path}，跳過")
        notice_skipped = True
    else:
        notice_path.write_text(NOTICE_DEFAULT, encoding="utf-8")
        print(f"已生成 {notice_path}")

    japanese_name = get_japanese_name(folder)
    display_text = f"{name}({japanese_name})" if japanese_name else name
    root_updated = update_root_index(name, display_text)

    msg_lines = [f"✓ 作品資料夾：{name}"]
    msg_lines.append(f"✓ index.html 已生成")
    msg_lines.append(f"{'（已存在，跳過）' if notice_skipped else '✓'} notice.txt")
    msg_lines.append(f"{'✓ 根首頁目錄已更新' if root_updated else '（根首頁連結已存在，跳過）'}")
    messagebox.showinfo("完成", "\n".join(msg_lines))


if __name__ == "__main__":
    main()
