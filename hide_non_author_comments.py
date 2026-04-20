import re
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# 隱藏非作者留言的處理函數
def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 移除既有的隱藏用 span 標籤（正常形式，保留包住的內容），不影響上色用的 span
    content = re.sub(r'<span style="display:none;">(.*?)</span>', r'\1', content, flags=re.DOTALL)

    # 移除被編輯器 HTML 編碼的孤兒版本（直接刪除，無對應內容包覆關係）
    content = content.replace('&lt;span style=&quot;display:none;&quot;&gt;', '')
    content = content.replace('&lt;/span&gt;', '')

    lines = content.splitlines(keepends=True)

    # 匹配留言標頭的正規表達式
    header_pattern = re.compile(r"^(\d+)\s*：\s*(.*?)\s*：\s*(\d{4}/\d{2}/\d{2}.*?ID:.*)$")
    
    out_lines = []
    in_non_author = False
    
    for line in lines:
        m = header_pattern.match(line)
        if m:
            name = m.group(2)
            # 判斷是否為作者留言
            if "◆pRBMvKqQmw" in name:
                # 若之前在非作者留言區塊中，則關閉 span 標籤
                if in_non_author:
                    out_lines[-1] = out_lines[-1] + '</span>'
                    in_non_author = False
                out_lines.append(line)
            else:
                # 這是非作者留言
                if not in_non_author:
                    in_non_author = True
                    # 在這行最前面加上隱藏用的 span 標籤
                    out_lines.append('<span style="display:none;">' + line)
                else:
                    # 連續的非作者留言，保持在 span 內
                    out_lines.append(line)
        else:
            out_lines.append(line)
    
    # 檔案結尾時若還在非作者留言區塊內，需補上關閉的 span 標籤
    if in_non_author:
        out_lines[-1] = out_lines[-1] + '</span>'

    # 覆寫原本的檔案
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

def main():
    root = tk.Tk()
    root.withdraw() # 隱藏主視窗
    
    # 跳出選擇檔案視窗 (可複選)
    file_paths = filedialog.askopenfilenames(
        title="選擇要處理的 AA HTML 檔案",
        filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")]
    )
    
    if not file_paths:
        print("未選擇任何檔案，結束執行。")
        return
        
    success_count = 0
    errors = []
    
    for fp in file_paths:
        try:
            process_file(fp)
            success_count += 1
        except Exception as e:
            errors.append(f"{os.path.basename(fp)}: {e}")
            
    m_body = f"處理完畢！成功處理 {success_count} 個檔案。"
    if errors:
        m_body += f"\n\n失敗檔案 ({len(errors)}):\n" + "\n".join(errors)
        
    messagebox.showinfo("執行結果", m_body)

if __name__ == '__main__':
    main()
