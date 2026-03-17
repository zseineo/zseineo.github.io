#!/bin/bash
# strip-annotations.sh
# 移除所有網頁的標記系統，保留底色設定
# 執行方式：在專案根目錄執行 bash strip-annotations.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUBLIC_DIR="$SCRIPT_DIR/public"

# 替換用的 inline 底色腳本（單行，避免 sed 換行問題）
BG_SCRIPT='<script>var c=localStorage.getItem("pagebgColor");if(c)document.body.style.backgroundColor=c;<\/script>'

echo "=== 移除標記系統 ==="
echo ""

removed=0
skipped=0

for f in "$PUBLIC_DIR"/*.html; do
  [ -f "$f" ] || continue
  name=$(basename "$f")

  if ! grep -q "annotation.js" "$f"; then
    echo "  - $name（無標記系統，略過）"
    skipped=$((skipped + 1))
    continue
  fi

  # 移除 annotation.js 的 script 標籤
  sed -i '/annotation\.js/d' "$f"

  # 若尚未有底色腳本，在 </body> 前插入
  if ! grep -q "pagebgColor" "$f"; then
    sed -i "s|</body>|${BG_SCRIPT}\n</body>|" "$f"
  fi

  echo "  ✓ $name"
  removed=$((removed + 1))
done

echo ""
echo "→ 已處理 $removed 個檔案，略過 $skipped 個"
echo ""
echo "完成。annotation.js 本身仍保留在專案中，"
echo "若確定不再需要可手動刪除，或執行 sync.sh 重新啟用標記系統。"
