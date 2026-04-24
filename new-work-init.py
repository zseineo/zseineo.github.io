#!/usr/bin/env python3
"""
初始化新作品資料夾，生成 index.html 與 notice.txt，並自動寫入根首頁目錄。

用法：
    python new-work-init.py <作品名稱>

例子：
    python new-work-init.py 亞魯夫的異世界轉移冒險者傳記

作品資料夾會建立在 gallery/<作品名稱>/ 底下。
"""
import sys
import re
from pathlib import Path

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


def update_root_index(name: str) -> bool:
    """在根首頁 <ul> 末端插入新作品連結，若已存在則跳過。回傳是否有寫入。"""
    if not ROOT_INDEX.exists():
        print(f"！找不到根首頁 {ROOT_INDEX}，跳過自動寫入")
        return False

    content = ROOT_INDEX.read_text(encoding="utf-8")
    href = f"gallery/{name}/"

    if href in content:
        print(f"根首頁已有 {name} 的連結，跳過")
        return False

    new_item = f'    <li><a href="{href}">{name}</a></li>'
    # 在 </ul> 前插入（只改第一個 </ul>，即作品列表那個）
    updated = re.sub(r'[ \t]*</ul>', f"{new_item}\n  </ul>", content, count=1)
    if updated == content:
        print("！找不到 </ul>，無法自動寫入根首頁")
        return False

    ROOT_INDEX.write_text(updated, encoding="utf-8")
    print(f"已在根首頁目錄加入：{name}")
    return True


def main():
    if len(sys.argv) < 2:
        print(f"用法：python {sys.argv[0]} <作品名稱>")
        sys.exit(1)

    name = sys.argv[1]

    if name in RESERVED_NAMES:
        print(f"錯誤：'{name}' 為保留名稱，不可作為作品名")
        sys.exit(1)

    folder = GALLERY_DIR / name

    if not folder.exists():
        folder.mkdir(parents=True)
        print(f"已建立資料夾 {folder}")

    if not folder.is_dir():
        print(f"錯誤：{folder} 不是資料夾")
        sys.exit(1)

    title = name
    index_path = folder / "index.html"
    notice_path = folder / "notice.txt"

    index_path.write_text(build_index(folder, title), encoding="utf-8")
    print(f"已生成 {index_path}")

    if notice_path.exists():
        print(f"已存在 {notice_path}，跳過")
    else:
        notice_path.write_text(NOTICE_DEFAULT, encoding="utf-8")
        print(f"已生成 {notice_path}")

    update_root_index(name)


if __name__ == "__main__":
    main()
