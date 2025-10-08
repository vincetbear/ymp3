"""
YouTube Cookies 設定輔助腳本
用於將 cookies 檔案轉換為 Railway 環境變數格式
"""

import base64
import os
import sys

def convert_cookies_to_base64(cookies_file_path):
    """將 cookies 檔案轉換為 base64 編碼"""
    try:
        # 讀取 cookies 檔案
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 轉換為 base64
        content_bytes = content.encode('utf-8')
        base64_content = base64.b64encode(content_bytes).decode('utf-8')
        
        return base64_content
    except FileNotFoundError:
        print(f"❌ 錯誤: 找不到檔案 '{cookies_file_path}'")
        return None
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return None

def save_to_file(base64_content, output_file='cookies_base64.txt'):
    """儲存 base64 內容到檔案"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(base64_content)
        print(f"✅ Base64 內容已儲存到: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 儲存失敗: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("YouTube Cookies 轉換工具")
    print("=" * 60)
    print()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        cookies_file = sys.argv[1]
    else:
        # 互動式輸入
        print("請提供 YouTube cookies 檔案路徑:")
        print("(或直接拖曳檔案到此視窗)")
        cookies_file = input("檔案路徑: ").strip().strip('"')
    
    if not cookies_file:
        print("❌ 未提供檔案路徑")
        return
    
    print(f"\n📁 處理檔案: {cookies_file}")
    
    # 轉換為 base64
    base64_content = convert_cookies_to_base64(cookies_file)
    
    if not base64_content:
        return
    
    print(f"✅ 轉換成功!")
    print(f"📊 Base64 長度: {len(base64_content)} 字元")
    
    # 儲存到檔案
    output_file = 'cookies_base64.txt'
    save_to_file(base64_content, output_file)
    
    # 顯示使用說明
    print("\n" + "=" * 60)
    print("📝 下一步:")
    print("=" * 60)
    print()
    print("1. 開啟 Railway Dashboard:")
    print("   https://railway.app")
    print()
    print("2. 選擇你的專案 (ymp3)")
    print()
    print("3. 進入 Settings → Variables")
    print()
    print("4. 新增環境變數:")
    print("   變數名稱: YOUTUBE_COOKIES_B64")
    print(f"   變數值: (複製 {output_file} 的內容)")
    print()
    print("5. 儲存並等待自動重新部署")
    print()
    print("=" * 60)
    print()
    
    # 詢問是否複製到剪貼簿
    try:
        import pyperclip
        copy = input("是否要複製 Base64 內容到剪貼簿? (y/n): ").lower()
        if copy == 'y':
            pyperclip.copy(base64_content)
            print("✅ 已複製到剪貼簿!")
    except ImportError:
        print("💡 提示: 安裝 pyperclip 套件可直接複製到剪貼簿")
        print("   pip install pyperclip")
    except Exception as e:
        print(f"⚠️ 無法複製到剪貼簿: {str(e)}")
    
    print("\n✅ 完成!")

if __name__ == '__main__':
    main()
