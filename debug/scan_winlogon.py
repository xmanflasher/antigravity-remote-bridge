import ctypes
import win32service
import win32con
import win32process
import win32gui

def enumerate_winlogon_desktop():
    print("Attempting to open Winlogon desktop...")
    
    # Define the callback function for EnumDesktopWindows
    def enum_callback(hwnd, lparam):
        try:
            name = win32gui.GetWindowText(hwnd)
            cls = win32gui.GetClassName(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            print(f"  - HWND: {hwnd} | Class: {cls} | Text: '{name}' | Visible: {visible}")
            
            # Recurse into children
            def child_callback(child_hwnd, _):
                c_name = win32gui.GetWindowText(child_hwnd)
                c_cls = win32gui.GetClassName(child_hwnd)
                if c_name or c_cls == "Button":
                    print(f"    - Child: {child_hwnd} | Class: {c_cls} | Text: '{c_name}'")
            
            win32gui.EnumChildWindows(hwnd, child_callback, None)
        except:
            pass
        return True

    try:
        # 1. Open the 'Winlogon' desktop
        h_desk = ctypes.windll.user32.OpenDesktopW("Winlogon", 0, False, win32con.MAXIMUM_ALLOWED)
        if not h_desk:
            print(f"Failed to open Winlogon desktop. Error: {ctypes.GetLastError()}")
            return

        # 2. Iterate through windows on that desktop
        print("\n--- Listing windows on Winlogon desktop ---")
        # Note: EnumDesktopWindows takes the handle to the desktop
        # We need to use the ctypes version or ensure win32gui can handle it
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        
        def _callback(hwnd, lparam):
            return enum_callback(hwnd, lparam)

        ctypes.windll.user32.EnumDesktopWindows(h_desk, WNDENUMPROC(_callback), 0)
        
        ctypes.windll.user32.CloseDesktop(h_desk)
        print("\nDone.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    enumerate_winlogon_desktop()
