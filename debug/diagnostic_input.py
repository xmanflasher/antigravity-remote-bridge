import asyncio
import sys
import os
import time
import pygetwindow as gw
import pyautogui
from pywinauto import Application

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system_control import SystemController
from core.gui_control import GUIController

async def diagnostic():
    print("🔍 Starting Local Input Diagnosis (Copy & Paste)...")
    sys_ctrl = SystemController()
    gui_ctrl = GUIController(sys_ctrl)
    
    title = await sys_ctrl.find_antigravity_window()
    if not title:
        print("❌ Could not find target window.")
        return
    print(f"✅ Found window: {title}")
    
    # 1. Activation
    windows = gw.getWindowsWithTitle(title)
    if not windows: return
    win = windows[0]
    if win.isMinimized: win.restore()
    win.activate()
    time.sleep(1)
    
    # 2. Toggle Panel
    await gui_ctrl.open_agent_panel(title)
    time.sleep(1)
    
    # 3. Clipboard Injection
    print("🚀 Running Copy-Paste Injection test...")
    try:
        # This will call the newly updated gui_control method
        success = await gui_ctrl.enter_prompt("Diagnostic: Clipboard Paste Test Success", title)
        if success:
            print("✅ Injection logic completed successfully.")
        else:
            print("❌ Injection logic failed.")
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic())
