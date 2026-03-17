#!/bin/bash
# sync.sh - 執行方式：在專案根目錄執行 bash sync.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUBLIC_DIR="$SCRIPT_DIR/public"
INDEX="$SCRIPT_DIR/index.html"
ANNOTATION_TAG='<script type="module" src="../annotation.js"></script>'

echo "=== 開始同步 ==="

# ── 1. 檢查並補上 annotation.js 標記 ──────────────────────────
echo ""
echo "[1] 檢查 annotation.js 標記..."

added=0
for f in "$PUBLIC_DIR"/*.html; do
  [ -f "$f" ] || continue
  name=$(basename "$f")
  if grep -q "annotation.js" "$f"; then
    echo "  ✓ $name"
  else
    # 在 </body> 前插入 script 標籤
    sed -i "s|</body>|${ANNOTATION_TAG}\n</body>|" "$f"
    echo "  + $name（已補上標記）"
    added=$((added + 1))
  fi
done

echo "  → 共補上 $added 個檔案"

# ── 2. 更新 index.html 的連結清單 ─────────────────────────────
echo ""
echo "[2] 更新 index.html..."

# 收集所有 public/*.html，按檔名排序
list_items=""
count=0
for f in $(ls "$PUBLIC_DIR"/*.html 2>/dev/null | sort); do
  name=$(basename "$f" .html)
  list_items="${list_items}    <li><a href=\"public/${name}.html\">${name}</a></li>\n"
  count=$((count + 1))
done

if [ $count -eq 0 ]; then
  echo "  ! public/ 資料夾裡沒有 HTML 檔案"
  exit 1
fi

# 用 awk 替換 <ul>...</ul> 之間的內容
awk -v items="$list_items" '
  /<ul>/ { print; in_ul=1; printf "%s", items; next }
  /<\/ul>/ { in_ul=0 }
  in_ul { next }
  { print }
' "$INDEX" > "$INDEX.tmp" && mv "$INDEX.tmp" "$INDEX"

echo "  → index.html 已更新，共 $count 個連結"

echo ""
echo "=== 完成 ==="
