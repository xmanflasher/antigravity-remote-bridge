import pyautogui
import time
from PIL import Image

def detect_signin_button():
    print("Capturing screen for analysis...")
    time.sleep(1) # Wait for animation
    
    try:
        shot = pyautogui.screenshot()
        width, height = shot.size
        
        # We look in the middle horizontal area (center 40%) 
        # and bottom vertical area (50% to 90%)
        search_x_start = int(width * 0.3)
        search_x_end = int(width * 0.7)
        search_y_start = int(height * 0.5)
        search_y_end = int(height * 0.9)
        
        # Look for a specific color pattern or high-contrast box
        # The button in the photo is light-colored/white text on blue background
        # We can find the "Sign-in" button by looking for a horizontal block of 
        # pixels that differ significantly from the background blue.
        
        # 1. Sample background color at a "safe" spot
        bg_color = shot.getpixel((width // 10, height // 10))
        print(f"Sample Background Color: {bg_color}")
        
        # 2. Find pixels that are NOT the background color in our search zone
        diff_pixels = []
        for y in range(search_y_start, search_y_end, 5): # Step 5 for speed
            for x in range(search_x_start, search_x_end, 5):
                pix = shot.getpixel((x, y))
                # Simple distance in RGB space
                dist = sum(abs(a - b) for a, b in zip(pix, bg_color))
                if dist > 60: # Significant difference
                    diff_pixels.append((x, y))
        
        if not diff_pixels:
            print("No button-like pixels found.")
            return None
            
        # 3. Find the bounding box of the difference
        min_x = min(p[0] for p in diff_pixels)
        max_x = max(p[0] for p in diff_pixels)
        min_y = min(p[1] for p in diff_pixels)
        max_y = max(p[1] for p in diff_pixels)
        
        # The button is usually a smallish rectangle
        btn_width = max_x - min_x
        btn_height = max_y - min_y
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        print(f"Detected potential button area: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        print(f"Size: {btn_width}x{btn_height}, Center: ({center_x}, {center_y})")
        
        # Heuristic check: size should be reasonable
        if 50 < btn_width < 500 and 20 < btn_height < 200:
            print("Verdict: LIKELY BUTTON FOUND!")
            return (center_x, center_y)
        else:
            print("Verdict: Area found but size heuristic failed.")
            return None
            
    except Exception as e:
        print(f"Vision detection error: {e}")
        return None

if __name__ == "__main__":
    pos = detect_signin_button()
    if pos:
        print(f"READY_TO_CLICK:{pos[0]},{pos[1]}")
