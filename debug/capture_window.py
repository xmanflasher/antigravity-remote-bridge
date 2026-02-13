from pywinauto import Application
import pyautogui
import os

def capture_antigravity():
    try:
        title = "TopGun - Antigravity"
        print(f"Connecting to: {title}")
        app = Application(backend="uia").connect(title=title, class_name="Chrome_WidgetWin_1", timeout=5)
        window = app.window(title=title)
        
        # 確保視窗置頂
        window.set_focus()
        print("Window focused.")
        
        # 取得視窗座標
        rect = window.rectangle()
        print(f"Window Rect: {rect}")
        
        # 截圖 (這會擷取整個螢幕，然後我們可以根據 rect 切割)
        screenshot = pyautogui.screenshot()
        
        # 切割視窗區域 (left, top, right, bottom)
        window_img = screenshot.crop((rect.left, rect.top, rect.right, rect.bottom))
        
        output_path = "antigravity_screenshot.png"
        window_img.save(output_path)
        print(f"Screenshot saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_antigravity()
