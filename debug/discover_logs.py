import subprocess
import time
import os
import datetime

ANTIGRAVITY_BIN = r"D:\Antigravity\bin\antigravity.cmd"
APPDATA_PATH = os.path.join(os.environ['APPDATA'], 'Antigravity')

prompt = "請寫一個 Hello World 的 Python 檔案叫 real_test.py，然後結束任務。"

print(f"啟動 CLI: {prompt}")
process = subprocess.Popen(
    [ANTIGRAVITY_BIN, "chat", prompt],
    shell=True
)
process.wait()
print("CLI 已結束配合。正在監控 AppData 檔案變動...")

# 等待 15 秒讓 Agent 執行一些動作
for _ in range(3):
    time.sleep(5)
    now = datetime.datetime.now()
    one_minute_ago = now - datetime.timedelta(seconds=60)
    
    print(f"\n--- 檢查最近 60 秒變動的檔案 ({now.strftime('%H:%M:%S')}) ---")
    found = False
    for root, dirs, files in os.walk(APPDATA_PATH):
        for file in files:
            path = os.path.join(root, file)
            try:
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if mtime > one_minute_ago:
                    print(f"[{mtime.strftime('%H:%M:%S')}] {path} (Size: {os.path.getsize(path)})")
                    found = True
            except:
                continue
    if not found:
        print("沒有偵測到變動。")

print("\n測試結束。")
