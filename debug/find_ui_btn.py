from pywinauto import Desktop
import time

def find_signin_button():
    print("Searching for 'Sign-in' (登入) button...")
    try:
        # Try both 'uia' and 'win32' backends, though 'uia' is better for modern Windows
        d = Desktop(backend="uia")
        
        # Search for any button that contains '登' or 'Sign'
        buttons = d.windows(control_type="Button")
        print(f"Found {len(buttons)} total buttons on Desktop.")
        
        target = None
        for b in buttons:
            name = b.window_text()
            print(f" - Found button: '{name}' (Visible: {b.is_visible()})")
            if "登入" in name or "Sign" in name:
                target = b
                break
        
        if target:
            rect = target.rectangle()
            print(f"SUCCESS: Found button '{target.window_text()}' at {rect}")
            # Center of the rect
            center = ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            print(f"Center coordinates: {center}")
        else:
            print("FAILED: Could not find 'Sign-in' button in the UI tree.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_signin_button()
