import subprocess
import os

def test_antigravity_chat(prompt, proj_path):
    # 手動模擬 antigravity.cmd 的行為，並設定環境變數
    antigravity_exe = r"D:\Antigravity\Antigravity.exe"
    cli_js = r"D:\Antigravity\resources\app\out\cli.js"
    
    env = os.environ.copy()
    env["ELECTRON_RUN_AS_NODE"] = "1"
    
    cmd = f'"{antigravity_exe}" "{cli_js}" chat "{prompt}" --verbose'
    
    print(f"正在執行指令 (Node 模式): {cmd}")
    print(f"環境變數: ELECTRON_RUN_AS_NODE=1")
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=proj_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            env=env
        )
        
        print("\n--- 輸出日誌 ---")
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(f"> {line.strip()}")
        
        process.wait()
        print(f"\n🏁 任務結束，回傳碼: {process.returncode}")
            
    except Exception as e:
        print(f"❌ 發生異常: {e}")

if __name__ == "__main__":
    test_prompt = "列出 core/ 目錄下的檔案"
    test_path = r"d:\project\antigravity-remote-bridge"
    test_antigravity_chat(test_prompt, test_path)


