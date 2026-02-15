import pyautogui
import os
import time
from PIL import Image

def test_screenshot():
    print("Taking screenshot in 3 seconds...")
    # Give user time to lock screen if they want, but here we just test.
    # In my environment it's always locked.
    time.sleep(3)
    
    try:
        shot = pyautogui.screenshot()
        path = "debug_shot.png"
        shot.save(path)
        print(f"Screenshot saved to {path} (Size: {shot.size})")
        
        # Analyze if it's black
        colors = shot.getcolors(shot.size[0] * shot.size[1])
        if colors and len(colors) == 1 and colors[0][1] == (0, 0, 0):
            print("Verdict: Screenshot is PURE BLACK.")
        else:
            print(f"Verdict: Screenshot contains colors. (First 5 colors: {colors[:5] if colors else 'None'})")
            
    except Exception as e:
        print(f"Screenshot failed: {e}")

if __name__ == "__main__":
    test_screenshot()
