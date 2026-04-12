#!/usr/bin/env python3
# apply-monapo.py
#
# 選擇 AA HTML 檔案，注入 JS 字型偵測：
# 當瀏覽器偵測不到 MS PGothic 時，自動把 <pre> 改成使用 Monapo。
# 桌機（有 MS PGothic 的環境）完全不受影響。
#
# 執行方式：python apply-monapo.py

import os, sys, re

# Windows 終端機編碼相容（日文字元等）
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT  = os.path.dirname(os.path.abspath(__file__))
FONT_FILE  = os.path.join(REPO_ROOT, 'fonts', 'monapo.ttf')
EXCLUDE_DIRS = {'fonts', 'private', 'working', '.git'}

# 用 marker 包夾插入內容，方便重複執行時清除舊版
CSS_MARK_S  = '/* monapo:start */'
CSS_MARK_E  = '/* monapo:end */'
HTML_MARK_S = '<!-- monapo:start -->'
HTML_MARK_E = '<!-- monapo:end -->'


# ──────────────────────────────────────────────────────────────
# 工具函式
# ──────────────────────────────────────────────────────────────

def font_rel_path(html_file):
    """計算從 html_file 到 fonts/monapo.ttf 的相對路徑（正斜線）"""
    rel = os.path.relpath(FONT_FILE, os.path.dirname(html_file))
    return rel.replace('\\', '/')


def strip_existing_monapo(content):
    """
    移除任何現存的 Monapo 修改：
      1. marker 包夾的區塊（新版）
      2. 沒有 marker 的舊版 @font-face 與 font-family 屬性
    """
    # 1. CSS marker 區塊
    content = re.sub(
        r'[ \t]*' + re.escape(CSS_MARK_S) + r'[\s\S]*?' + re.escape(CSS_MARK_E) + r'[ \t]*\n?',
        '',
        content,
    )
    # 2. HTML marker 區塊
    content = re.sub(
        r'[ \t]*' + re.escape(HTML_MARK_S) + r'[\s\S]*?' + re.escape(HTML_MARK_E) + r'[ \t]*\n?',
        '',
        content,
    )
    # 3. 舊版無 marker 的 @font-face Monapo 區塊
    content = re.sub(
        r'[ \t]*@font-face\s*\{[^{}]*[\'"]Monapo[\'"][^{}]*\}[ \t]*\n?',
        '',
        content,
    )
    # 4. CSS 規則中含 Monapo 的 font-family 屬性行
    content = re.sub(
        r'[ \t]*font-family\s*:\s*[\'"]Monapo[\'"][^;]*;[ \t]*\n?',
        '',
        content,
    )
    # 5. 收斂連續多餘空行
    content = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', content)
    return content


# ──────────────────────────────────────────────────────────────
# 核心修改邏輯
# ──────────────────────────────────────────────────────────────

def apply_monapo(html_path):
    """
    修改單一 HTML 檔案。每次執行都會先清除舊版修改，再重新套用。
    回傳 ('ok'|'error', 訊息)
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        original = f.read()

    content = original
    notes = []

    # ── 0. 清除舊版修改（不論有無 marker）──
    cleaned = strip_existing_monapo(content)
    if cleaned != content:
        notes.append('清除舊版')
    content = cleaned

    path = font_rel_path(html_path)

    # ── 1. 確保 viewport meta 存在 ──
    if not re.search(r'<meta\s+[^>]*name\s*=\s*["\']viewport["\']', content, re.IGNORECASE):
        viewport_tag = '\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
        charset_m = re.search(r'<meta\s+[^>]*charset[^>]*>', content, re.IGNORECASE)
        if charset_m:
            ins = charset_m.end()
        else:
            head_m = re.search(r'<head[^>]*>', content, re.IGNORECASE)
            if not head_m:
                return 'error', '找不到 <head> 標籤'
            ins = head_m.end()
        content = content[:ins] + viewport_tag + content[ins:]
        notes.append('補上 viewport')

    # ── 2. 在 <style> 後插入 @font-face（用 marker 包夾）──
    style_open = re.search(r'<style[^>]*>', content)
    if not style_open:
        return 'error', '找不到 <style> 標籤'

    font_face_block = (
        f"\n    {CSS_MARK_S}\n"
        "    @font-face {\n"
        "        font-family: 'Monapo';\n"
        f"        src: url('{path}') format('truetype');\n"
        "        font-weight: normal;\n"
        "        font-style: normal;\n"
        "        font-display: swap;\n"
        "    }\n"
        f"    {CSS_MARK_E}"
    )
    ins = style_open.end()
    content = content[:ins] + font_face_block + content[ins:]

    # ── 3. 在 </body> 前插入 JS 字型偵測腳本（用 marker 包夾）──
    js_block = f"""
{HTML_MARK_S}
<script>
(function() {{
    // 偵測系統是否有 MS PGothic：
    // 比較 'MS PGothic' 與純 monospace 渲染同一字串的寬度，
    // 如果不同，代表 MS PGothic 確實存在。
    function hasMSPGothic() {{
        var c = document.createElement('canvas');
        var ctx = c.getContext('2d');
        var test = 'あいうえおWMHIabc';
        ctx.font = "16px monospace";
        var baseW = ctx.measureText(test).width;
        ctx.font = "16px 'MS PGothic', monospace";
        var fontW = ctx.measureText(test).width;
        return Math.abs(baseW - fontW) > 1;
    }}

    if (hasMSPGothic()) return;  // 系統有 MS PGothic，直接用，不替換

    // 沒有 MS PGothic：等 Monapo 載入後再套用，避免跳字
    function applyMonapo() {{
        var pres = document.querySelectorAll('pre');
        for (var i = 0; i < pres.length; i++) {{
            pres[i].style.fontFamily = "'Monapo', 'MS PGothic', monospace";
        }}
    }}

    if (document.fonts && document.fonts.load) {{
        document.fonts.load("16px 'Monapo'").then(applyMonapo, applyMonapo);
    }} else {{
        applyMonapo();
    }}
}})();
</script>
{HTML_MARK_E}
"""
    body_close = content.rfind('</body>')
    if body_close != -1:
        content = content[:body_close] + js_block + content[body_close:]
    else:
        content = content + js_block

    # ── 4. 寫入 ──
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    msg = '已套用'
    if notes:
        msg += '（' + '、'.join(notes) + '）'
    return 'ok', msg


# ──────────────────────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────────────────────

def main():
    print('=' * 62)
    print('  Monapo 字型套用工具（JS 字型偵測版）')
    print('  有 MS PGothic 的環境：不變動')
    print('  沒有 MS PGothic 的環境：自動切換為 Monapo')
    print('=' * 62)

    if not os.path.exists(FONT_FILE):
        print(f'\n[錯誤] 找不到字型檔：fonts/monapo.ttf')
        sys.exit(1)

    # Windows 檔案選擇視窗
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

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
    ok = err = 0
    for fp in selected:
        rel = os.path.relpath(fp, REPO_ROOT).replace('\\', '/')
        status, msg = apply_monapo(fp)
        icon = {'ok': '✓', 'error': '✗'}[status]
        print(f'  {icon}  {rel}')
        print(f'       → {msg}')
        if status == 'ok':
            ok += 1
        else:
            err += 1

    print(f'\n完成：成功 {ok} 個 / 失敗 {err} 個')


if __name__ == '__main__':
    main()
