import ctypes
import time
import os

user32 = ctypes.windll.user32

def get_desktop_name(h_desktop):
    buffer = ctypes.create_unicode_buffer(256)
    # UOI_NAME = 2
    if user32.GetUserObjectInformationW(h_desktop, 2, buffer, ctypes.sizeof(buffer), None):
        return buffer.value
    return "Unknown"

def test_methods():
    print(f"--- Diagnostic Run at {time.ctime()} ---")
    
    # Method 1: GetForegroundWindow
    hwnd = user32.GetForegroundWindow()
    print(f"[1] GetForegroundWindow: {hwnd}")
    if hwnd != 0:
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buffer, 256)
        print(f"    Window Title: '{buffer.value}'")

    # Method 2: SwitchDesktop
    # DESKTOP_SWITCHDESKTOP = 0x01
    h_default = user32.OpenDesktopW("Default", 0, False, 0x01)
    if h_default:
        result = user32.SwitchDesktop(h_default)
        print(f"[2] SwitchDesktop('Default'): {result} (1=Success/Unlocked, 0=Fail/Locked)")
        user32.CloseDesktop(h_default)
    else:
        print("[2] OpenDesktopW('Default') failed.")

    # Method 4: WTSQuerySessionInformation (SessionFlags)
    # WTS_CURRENT_SERVER_HANDLE = 0, WTS_CURRENT_SESSION = -1, WTSSessionInfoEx = 25
    WTS_CURRENT_SERVER_HANDLE = 0
    WTS_CURRENT_SESSION = -1
    WTSSessionInfoEx = 25
    
    ppBuffer = ctypes.c_void_p()
    pBytesReturned = ctypes.c_ulong()
    
    if ctypes.windll.wtsapi32.WTSQuerySessionInformationW(
        WTS_CURRENT_SERVER_HANDLE, WTS_CURRENT_SESSION, WTSSessionInfoEx, 
        ctypes.byref(ppBuffer), ctypes.byref(pBytesReturned)
    ):
        # WTSINFOEX structure
        # Level (DWORD) + Data (WTSINFOEX_LEVEL1)
        # WTSINFOEX_LEVEL1 (SessionId, SessionState, SessionFlags)
        # SessionFlags: 0=Lock, 1=Unlock
        if pBytesReturned.value > 0:
            # Shift 4 bytes for Level, then 8 bytes for SessionId/SessionState to reach SessionFlags
            # Actually Level is 4 bytes, SessionId 4, SessionState 4, SessionFlags 4
            # Struct: Level (4), SessionId (4), SessionState (4), SessionFlags (4)
            pData = ctypes.cast(ppBuffer, ctypes.POINTER(ctypes.c_uint))
            # Level is 1 (Level1)
            level = pData[0]
            if level == 1:
                session_flags = pData[3] 
                state_str = {0: "LOCKED", 1: "UNLOCKED"}.get(session_flags, f"UNKNOWN ({session_flags})")
                print(f"[4] WTS SessionFlags: {session_flags} ({state_str})")
            else:
                print(f"[4] WTS Level {level} not handled.")
        
        ctypes.windll.wtsapi32.WTSFreeMemory(ppBuffer)
    else:
        print("[4] WTSQuerySessionInformation failed.")

    print("-" * 30)


if __name__ == "__main__":
    print("Script started. I will run 5 iterations every 5 seconds.")
    print("Please LOCK your computer after the first iteration to see the difference.")
    for i in range(5):
        print(f"\nIteration {i+1}/5")
        test_methods()
        time.sleep(5)
