import pygetwindow as gw
import pyautogui
import os

def capture_fast():
    try:
        title = "TopGun - Antigravity"
        print(f"Searching for: {title}")
        windows = gw.getWindowsWithTitle(title)
        if not windows:
            print("Window not found.")
            return
        
        win = windows[0]
        print(f"Found window: {win.title} at ({win.left}, {win.top}, {win.width}, {win.height})")
        
        # 不要 set_focus，直接截取該區域
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        output_path = "antigravity_screenshot.png"
        screenshot.save(output_path)
        print(f"Screenshot saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_fast()
