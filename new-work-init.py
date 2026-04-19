#!/usr/bin/env python3
"""
初始化新作品資料夾，生成 index.html 與 notice.txt。

用法：
    python new-work-init.py <資料夾路徑> <作品標題>

例子：
    python new-work-init.py "亞魯夫的異世界轉移冒險者傳記" "亞魯夫的異世界轉移冒險者傳記"
"""
import sys
import re
from pathlib import Path

NOTICE_DEFAULT = "作者 \n翻譯 Gemini 3.1\n"


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
  <a class="back" href="../">← 返回首頁</a>
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


def main():
    if len(sys.argv) < 3:
        print(f"用法：python {sys.argv[0]} <資料夾路徑> <作品標題>")
        sys.exit(1)

    folder = Path(sys.argv[1])
    title = sys.argv[2]

    if not folder.is_dir():
        print(f"錯誤：找不到資料夾 {folder}")
        sys.exit(1)

    index_path = folder / "index.html"
    notice_path = folder / "notice.txt"

    index_path.write_text(build_index(folder, title), encoding="utf-8")
    print(f"已生成 {index_path}")

    if notice_path.exists():
        print(f"已存在 {notice_path}，跳過")
    else:
        notice_path.write_text(NOTICE_DEFAULT, encoding="utf-8")
        print(f"已生成 {notice_path}")


if __name__ == "__main__":
    main()
