import asyncio
from pywinauto import Application
from core.system_control import SystemController
import win32gui

def list_win32_children(hwnd):
    results = []
    def callback(child_hwnd, _):
        title = win32gui.GetWindowText(child_hwnd)
        cls = win32gui.GetClassName(child_hwnd)
        results.append((child_hwnd, title, cls))
        return True
    win32gui.EnumChildWindows(hwnd, callback, None)
    return results

async def debug_win32():
    sys_ctrl = SystemController()
    title = await sys_ctrl.find_antigravity_window()
    if not title: return
    
    print(f"✅ Window: {title}")
    
    # Use win32 backend
    try:
        app = Application(backend="win32").connect(title=title, timeout=2)
        win = app.window(title=title)
        handle = win.handle
        
        print(f"📝 Handle: {handle}")
        children = list_win32_children(handle)
        print(f"📊 Found {len(children)} win32 children.")
        
        for i, (h, t, c) in enumerate(children[:50]): # First 50
            print(f"[{i}] HWND: {h} | Title: '{t}' | Class: '{c}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_win32())
