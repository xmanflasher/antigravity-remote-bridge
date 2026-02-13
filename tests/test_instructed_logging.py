import subprocess
import time
import os

ANTIGRAVITY_BIN = r"D:\Antigravity\bin\antigravity.cmd"
LOG_FILE = "bridge_test_log.txt"

# 清除舊的 Log
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

prompt = f"請列出當前目錄檔案，並將你的每一步思考與執行的工具輸出詳細記錄到 {LOG_FILE} 檔案中。"

print(f"發送指令: {prompt}")

# 執行 CLI
process = subprocess.Popen(
    [ANTIGRAVITY_BIN, "chat", prompt, "--verbose"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    shell=True
)

stdout, stderr = process.communicate()

print("CLI 已結束。等待 Agent 在 IDE 中完成任務...")

# 持續檢查 Log 檔案一段時間
for i in range(30):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if content:
                print(f"\n--- 偵測到 Log 內容 ({i}s) ---")
                print(content)
                print("--- Log 結束 ---")
    time.sleep(2)

print("\n測試結束。")
