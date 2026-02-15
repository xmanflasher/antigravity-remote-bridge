import time
import asyncio
import pyautogui
import ctypes
import win32api
import win32con
import os
from datetime import datetime

# Import is_screen_locked logic directly to avoid module issues
pyautogui.FAILSAFE = False

def is_locked():
    try:
        import subprocess
        cmd = 'tasklist /FI "IMAGENAME eq LogonUI.exe" /NH'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        if "LogonUI.exe" in output:
            return True
        h_desktop = ctypes.windll.user32.OpenInputDesktop(0, False, 0x01)
        if h_desktop:
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetUserObjectInformationW(h_desktop, 2, buffer, ctypes.sizeof(buffer), None)
            name = buffer.value
            ctypes.windll.user32.CloseDesktop(h_desktop)
            if name.lower() != "default":
                return True
        else:
            if ctypes.GetLastError() == 5:
                return True
        return False 
    except:
        return True

def win32_click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def log_state(step_name):
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"debug/unlock_logs/{timestamp}_{step_name}.png"
    try:
        pyautogui.screenshot(filename)
        print(f"  [LOG] Screenshot saved: {filename}")
    except Exception as e:
        print(f"  [LOG] Screenshot failed: {e}")

async def test_unlock_methods():
    print("--- 🚀 Advanced Unlock Solver 🚀 ---")
    print("Waiting for you to MANUALLY LOCK (Win+L) your machine...")
    
    while not is_locked():
        time.sleep(1)
        
    print("\n[!] LOCK DETECTED! Starting solver in 8 seconds (stabilizing)...")
    time.sleep(8)
    
    width, height = pyautogui.size()
    mid_x = width // 2
    
    methods = [
        ("Method A: Wake and Enter", [
            ('press', 'space'), ('sleep', 3), ('press', 'enter'), ('sleep', 1), ('press', 'space')
        ]),
        ("Method B: Direct Click and Multi-Enter", [
            ('press', 'esc'), ('sleep', 1),
            ('click', (mid_x, int(height*0.65))), ('sleep', 1),
            ('press', 'enter'), ('sleep', 0.5), ('press', 'enter')
        ]),
        ("Method C: Grid Sweep", [
            ('grid_click', (mid_x, int(height*0.5), int(height*0.8))),
            ('press', 'enter'), ('sleep', 1), ('press', 'space')
        ]),
        ("Method D: Tab Traversal", [
            ('press', 'space'), ('sleep', 2),
            ('press', 'tab'), ('sleep', 0.5), ('press', 'enter')
        ])
    ]

    for name, actions in methods:
        print(f"\n>> TESTING: {name}")
        log_state(f"START_{name.split(':')[0]}")
        
        for action, val in actions:
            if action == 'press':
                pyautogui.press(val)
                print(f"  Action: Press {val}")
            elif action == 'sleep':
                time.sleep(val)
            elif action == 'click':
                win32_click(val[0], val[1])
                print(f"  Action: Win32 Click at {val}")
            elif action == 'grid_click':
                x, y_start, y_end = val
                for y in range(y_start, y_end, 50):
                    win32_click(x, y)
                    time.sleep(0.1)
                print(f"  Action: Grid Click center column")
            
            time.sleep(1)
            if not is_locked():
                print(f"\n🎉🎉🎉 SUCCESS !!! {name} WORKED! 🎉🎉🎉")
                log_state("SUCCESS_FINAL")
                return
        
        print(f"  -- {name} failed. Still locked.")
        log_state(f"FAILED_{name.split(':')[0]}")
        time.sleep(2)

    print("\n❌ All automated attempts failed.")
    print("Please unlock manually to resume.")

if __name__ == "__main__":
    asyncio.run(test_unlock_methods())
