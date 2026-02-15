import pygetwindow as gw
import pyautogui
import win32gui
import win32con
import time
import asyncio
import ctypes
from ctypes import wintypes
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

    @staticmethod
    def is_screen_locked():
        """
        偵測 Windows 是否處於鎖定狀態。
        多層次偵測邏輯：
        1. 檢查 LogonUI.exe 程序是否存在 (鎖定畫面必備程序)。
        2. 檢查目前輸入桌面 (Input Desktop) 名稱是否為 "Default"。
        """
        try:
            # 層次 1: 檢查 LogonUI.exe 程序 (鎖定畫面的 UI 程序)
            import subprocess
            # /NH 代表不包含標頭
            cmd = 'tasklist /FI "IMAGENAME eq LogonUI.exe" /NH'
            # 使用 shell=True 確保環境變數正確，並補捉輸出
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
            if "LogonUI.exe" in output:
                return True

            # 層次 2: 檢查輸入桌面控制代碼與名稱
            # 0x01 = DESKTOP_SWITCHDESKTOP
            h_desktop = ctypes.windll.user32.OpenInputDesktop(0, False, 0x01)
            if h_desktop:
                buffer = ctypes.create_unicode_buffer(256)
                # UOI_NAME = 2
                ctypes.windll.user32.GetUserObjectInformationW(h_desktop, 2, buffer, ctypes.sizeof(buffer), None)
                name = buffer.value
                ctypes.windll.user32.CloseDesktop(h_desktop)
                
                # 如果目前的桌面不是 "Default"，則代表處於鎖定畫面 (例如名稱為 Winlogon)
                if name.lower() != "default":
                    return True
            else:
                # 如果無法開啟輸入桌面且錯誤碼為 5 (Access Denied)，通常表示桌面已被鎖定
                if ctypes.GetLastError() == 5:
                    return True
            
            return False 
        except Exception as e:
            print(f"⚠️ Lock detection failed: {e}")
            return False





    @staticmethod
    async def lock_screen():
        """鎖定 Windows 系統"""
        def _lock():
            try:
                ctypes.windll.user32.LockWorkStation()
                return True
            except Exception as e:
                print(f"❌ Lock failed: {e}")
                return False
        return await asyncio.to_thread(_lock)

    @staticmethod
    async def unlock_screen():
        """
        嘗試解除鎖定（喚醒螢幕並點擊登入）。
        針對兩階段流程優化：
        1. 鎖定畫面 (Wallpaper) -> 點擊喚醒
        2. 登入畫面 (Blue Screen) -> 點擊登入
        """
        def _unlock():
            try:
                # 步驟 1: 進到藍屏 (Wake up to Blue Screen)
                print("Step 1: Waking up to blue screen...")
                pyautogui.press('space')
                # 給予充足時間讓桌布完全滑動並載入 UI 元素
                time.sleep(5.0) 

                # 步驟 2: 用 Tab 在 UI 中找到登入鍵 (Navigate to Sign-in button)
                print("Step 2: Using Tab to navigate focus to Sign-in button...")
                # 通常按下 Space 喚醒後，焦點可能在別處，按一下 Tab 來嘗試導航到按鈕
                pyautogui.press('tab')
                time.sleep(1.0)

                # 步驟 3: Space/Enter (Trigger sign-in)
                print("Step 3: Triggering sign-in with Enter...")
                pyautogui.press('enter')
                time.sleep(1.0)
                
                # 額外保險：如果一次 Tab 不夠，嘗試第二次 Tab 並補上 Space
                # 這是為了應對可能存在的「選擇使用者」或「無障礙」按鈕
                print("Optional: Additional Tab/Space cycle for redundancy...")
                pyautogui.press('tab')
                time.sleep(0.5)
                pyautogui.press('space')
                
                print("🔓 Unlock sequence complete (1. Blue screen 2. Tab 3. Space/Enter).")





                return True
            except Exception as e:
                print(f"❌ Unlock failed: {e}")




