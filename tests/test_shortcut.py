import pygetwindow as gw
import pyautogui
import time
import os

def test_ctrl_l():
    try:
        title = "TopGun - Antigravity"
        windows = gw.getWindowsWithTitle(title)
        if not windows:
            print("Window not found.")
            return
        
        win = windows[0]
        win.activate()
        time.sleep(1)
        
        print("Sending Ctrl+L...")
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(3) # 等待面板打開
        
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        output_path = "antigravity_after_ctrl_l.png"
        screenshot.save(output_path)
        print(f"Screenshot saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ctrl_l()
