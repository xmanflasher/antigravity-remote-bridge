import pygetwindow as gw
import pyautogui
import win32gui
import win32con
import time
import asyncio
class SystemController:
    @staticmethod
    async def switch_to_english_input():
        def _switch():
            try:
                hwnd = win32gui.GetForegroundWindow()
                # WM_INPUTLANGCHANGEREQUEST = 0x0050
                # 0x04090409 is US English
                win32gui.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, 0x04090409)
                # Clear any IME candidate window or state
                for _ in range(2):
                    pyautogui.press('esc')
                    time.sleep(0.05)
                print("⌨️ Forced English Layout + Cleared IME.")
            except Exception as e:
                print(f"⚠️ IME switch failed: {e}")
        await asyncio.to_thread(_switch)
        await asyncio.sleep(0.3)

    @staticmethod
    async def find_antigravity_window(target_project=None):
        def _find():
            all_titles = gw.getAllTitles()
            
            # Priority 1: Exact match with project hint
            if target_project:
                # Typically titles are like "project_name - Antigravity"
                for t in all_titles:
                    if target_project in t and " - Antigravity" in t and "antigravity-remote-bridge" not in t:
                        return t

            # Priority 2: Generic " - Antigravity" suffix
            for t in all_titles:
                if " - Antigravity" in t and "antigravity-remote-bridge" not in t:
                    return t
            
            # Priority 3: Contains "Antigravity" but is not the bridge or Telegram
            for t in all_titles:
                if "Antigravity" in t and "antigravity-remote-bridge" not in t and "AntigravityConnect" not in t:
                    return t
            return None
        return await asyncio.to_thread(_find)

    @staticmethod
    async def activate_window(window_title):
        from pywinauto import Application
        
        def _activate():
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                return False # Changed from None to False for consistency with original return type
            
            win = windows[0]
            try:
                if win.isMinimized:
                    win.restore()
                
                # Using pywinauto's set_focus is often more robust than Win32 API
                try:
                    app = Application(backend="uia").connect(handle=win._hWnd, timeout=2)
                    app_win = app.window(handle=win._hWnd)
                    app_win.set_focus()
                except:
                    # Fallback to direct activation
                    win.activate()
                
                # Ensure it's foreground via Win32 as well
                try:
                    win32gui.SetForegroundWindow(win._hWnd)
                except Exception as e:
                    # print(f"⚠️ SetForegroundWindow failed (but continuing): {e}") # Removed print as per snippet
                    win32gui.ShowWindow(win._hWnd, win32con.SW_SHOW)
                    
                return True
            except Exception as e:
                print(f"❌ Window activation failed: {e}")
                return False
        
        return await asyncio.to_thread(_activate)

    @staticmethod
    def get_screen_size():
        return pyautogui.size()

    @staticmethod
    async def snap_window(window_title, side="left"):
        def _snap():
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                return False
            
            win = windows[0]
            screen_width, screen_height = pyautogui.size()
            
            half_width = screen_width // 2
            if side == "left":
                new_left, new_top = 0, 0
            else:
                new_left, new_top = half_width, 0
                
            # Resize and Move
            try:
                if win.isMinimized: win.restore()
                win.resizeTo(half_width, screen_height)
                win.moveTo(new_left, new_top)
                try:
                    win.activate()
                except:
                    pass # Non-critical if capture focus fails
                print(f"📏 Snapped window '{window_title}' to {side}.")
                return True
            except Exception as e:
                print(f"❌ Snapping failed: {e}")
                return False
        
        return await asyncio.to_thread(_snap)

    @staticmethod
    def launch_antigravity(proj_path):
        import subprocess
        import os
        try:
            proj_name = os.path.basename(proj_path)
            # 檢查是否已經有該專案視窗開啟
            all_titles = gw.getAllTitles()
            for t in all_titles:
                if proj_name in t and " - Antigravity" in t:
                    print(f"✅ Antigravity for {proj_name} is already running.")
                    return True
            
            cmd = f'antigravity "{proj_path}"'
            subprocess.Popen(cmd, shell=True, cwd=proj_path)
            print(f"🚀 Launched Antigravity for: {proj_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to launch Antigravity: {e}")
            return False
