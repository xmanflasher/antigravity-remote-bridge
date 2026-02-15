import ctypes
import time
from pywinauto import Desktop

def enum_winlogon_ui():
    print("Attempting to access Winlogon desktop...")
    try:
        # Layer 1: Try to list windows from the current context
        print("\n--- Listing windows in current context (UIA) ---")
        d_uia = Desktop(backend="uia")
        windows = d_uia.windows()
        for w in windows:
            print(f"  - [{w.process_id()}] {w.window_text()}")
            
        # Layer 2: Try to explicitly list buttons (Sign-in button is often a Button)
        buttons = d_uia.windows(control_type="Button")
        print(f"Found {len(buttons)} buttons.")
        for b in buttons:
            print(f"  - Button: '{b.window_text()}' (Visible: {b.is_visible()})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enum_winlogon_ui()
