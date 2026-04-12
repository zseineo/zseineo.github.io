#!/usr/bin/env python3
# apply-monapo.py
#
# 選擇 AA HTML 檔案，在手機 (@media max-width: 768px) 的 pre 規則中
# 加入 Monapo 字型。桌機維持原有字型不變。
#
# 執行方式：python apply-monapo.py

import os, sys, re

# Windows 終端機編碼相容（日文字元等）
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT  = os.path.dirname(os.path.abspath(__file__))
FONT_FILE  = os.path.join(REPO_ROOT, 'fonts', 'monapo.ttf')
DONE_MARK  = "font-family: 'Monapo'"   # 判斷是否已套用的標記
EXCLUDE_DIRS = {'fonts', 'private', 'working', '.git'}


# ──────────────────────────────────────────────────────────────
# 工具函式
# ──────────────────────────────────────────────────────────────

def font_rel_path(html_file):
    """計算從 html_file 到 fonts/monapo.ttf 的相對路徑（正斜線）"""
    rel = os.path.relpath(FONT_FILE, os.path.dirname(html_file))
    return rel.replace('\\', '/')


def find_matching_brace(text, open_pos):
    """從 open_pos（必須是 '{' 的位置）找出對應的 '}'，回傳其索引"""
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


# ──────────────────────────────────────────────────────────────
# 核心修改邏輯
# ──────────────────────────────────────────────────────────────

def apply_monapo(html_path):
    """
    修改單一 HTML 檔案。
    回傳 ('ok'|'skip'|'error', 訊息)
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        original = f.read()

    # 已套用過就跳過
    if DONE_MARK in original:
        return 'skip', '已套用，跳過'

    content = original
    path = font_rel_path(html_path)

    # ── 1. 在 <style> 後插入 @font-face ──
    style_open = re.search(r'<style>', content)
    if not style_open:
        return 'error', '找不到 <style> 標籤'

    font_face_block = (
        "\n    @font-face {"
        "\n        font-family: 'Monapo';"
        f"\n        src: url('{path}') format('truetype');"
        "\n        font-weight: normal;"
        "\n        font-style: normal;"
        "\n        font-display: swap;"
        "\n    }"
    )
    ins = style_open.end()
    content = content[:ins] + font_face_block + content[ins:]

    # ── 2. 找 @media (max-width: 768px) 區塊 ──
    media_m = re.search(r'@media\s*\(\s*max-width\s*:\s*768px\s*\)', content)

    if media_m:
        # 定位 media block 的開頭 '{'
        after    = content[media_m.end():]
        brace_in = after.index('{')
        m_open   = media_m.end() + brace_in           # '{' 的絕對位置
        m_close  = find_matching_brace(content, m_open)  # '}' 的絕對位置
        if m_close == -1:
            return 'error', '@media 區塊結構異常，找不到對應的 }'

        inner = content[m_open + 1 : m_close]

        # 在 inner 中找 pre { ... }（無巢狀大括號）
        pre_m = re.search(r'(pre\s*\{)([^}]*)(\})', inner)

        if pre_m:
            # 從現有屬性行偵測縮排量
            inner_lines = pre_m.group(2).split('\n')
            prop_indent = '            '   # fallback: 12 spaces
            for line in reversed(inner_lines):
                if line.strip():
                    prop_indent = re.match(r'^(\s*)', line).group(1)
                    break
            # 從 } 前的換行偵測 closing brace 縮排
            close_m = re.search(r'\n(\s*)\}$', pre_m.group(0))
            close_indent = close_m.group(1) if close_m else '        '

            props = pre_m.group(2).rstrip()
            if props and not props.rstrip().endswith(';'):
                props += ';'
            props += f"\n{prop_indent}font-family: 'Monapo', 'MS PGothic', monospace;\n{close_indent}"
            new_inner = (
                inner[: pre_m.start()]
                + pre_m.group(1)
                + props
                + pre_m.group(3)
                + inner[pre_m.end() :]
            )
        else:
            # @media 裡沒有 pre block，直接新增
            new_inner = (
                inner.rstrip()
                + "\n    pre {\n        font-family: 'Monapo', 'MS PGothic', monospace;\n    }\n"
            )

        content = content[: m_open + 1] + new_inner + content[m_close :]

    else:
        # 沒有 @media (max-width: 768px)，在 </style> 前新增整段
        style_close = content.rfind('</style>')
        if style_close == -1:
            return 'error', '找不到 </style> 標籤'
        mobile_rule = (
            "\n    @media (max-width: 768px) {"
            "\n        pre {"
            "\n            font-family: 'Monapo', 'MS PGothic', monospace;"
            "\n        }"
            "\n    }"
        )
        content = content[:style_close] + mobile_rule + '\n    ' + content[style_close:]

    # ── 3. 寫入 ──
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return 'ok', '已完成'


# ──────────────────────────────────────────────────────────────
# 檔案收集
# ──────────────────────────────────────────────────────────────

def collect_html_files():
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            if fn.lower().endswith(('.html', '.htm')):
                files.append(os.path.join(root, fn))
    return files


# ──────────────────────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────────────────────

def main():
    print('=' * 62)
    print('  Monapo 手機字型套用工具')
    print('  Desktop: keep original font  /  Mobile (<=768px): Monapo')
    print('=' * 62)

    if not os.path.exists(FONT_FILE):
        print(f'\n[錯誤] 找不到字型檔：fonts/monapo.ttf')
        sys.exit(1)

    # 用 Windows 檔案選擇視窗讓使用者選取
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()          # 隱藏主視窗
    root.attributes('-topmost', True)  # 確保對話框在最前面

    print('\n正在開啟檔案選擇視窗…（可複選）')

    selected = filedialog.askopenfilenames(
        title='選擇要套用 Monapo 的 HTML 檔案（可複選）',
        initialdir=REPO_ROOT,
        filetypes=[
            ('HTML 檔案', '*.html *.htm'),
            ('所有檔案',  '*.*'),
        ],
    )

    root.destroy()

    selected = list(selected)

    if not selected:
        print('未選擇任何檔案。')
        return

    print(f'\n正在修改 {len(selected)} 個檔案…\n')
    ok = skip = err = 0
    for fp in selected:
        rel    = os.path.relpath(fp, REPO_ROOT).replace('\\', '/')
        status, msg = apply_monapo(fp)
        icon = {'ok': '✓', 'skip': '－', 'error': '✗'}[status]
        print(f'  {icon}  {rel}')
        print(f'       → {msg}')
        if   status == 'ok':    ok   += 1
        elif status == 'skip':  skip += 1
        else:                   err  += 1

    print(f'\n完成：修改 {ok} 個 / 跳過 {skip} 個 / 失敗 {err} 個')


if __name__ == '__main__':
    main()
