import os
import asyncio
import pygetwindow as gw
import pyautogui
import pymsgbox
import time
import win32gui
import win32api
import win32con
from pywinauto import Application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class PermissionRelayMonitor:
    def __init__(self, bot, chat_id, window_title):
        self.bot = bot
        self.chat_id = chat_id
        self.window_title = window_title
        self.running = False
        self._task = None
        self.pending_buttons = {} 

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        print("🕵️ PermissionRelayMonitor started.")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
        print("🛑 PermissionRelayMonitor stopped.")

    async def _run_loop(self):
        while self.running:
            try:
                await self.check_permissions()
            except Exception as e:
                print(f"Relay Error: {e}")
            await asyncio.sleep(2) 

    async def check_permissions(self):
        try:
            app = Application(backend="uia").connect(title=self.window_title, timeout=1)
            window = app.window(title=self.window_title)
            
            # 更嚴格的關鍵字，避免抓到普通的切換按鈕
            target_keywords = ["Allow Once", "Allow", "Accept All", "Run", "全部接受", "允許"]
            
            # 使用 descendants 搜尋按鈕，且必須是可見的
            all_buttons = window.descendants(control_type="Button")
            for btn in all_buttons:
                try:
                    if not btn.is_visible() or not btn.is_enabled():
                        continue
                    
                    btn_text = btn.window_text()
                    if not btn_text: continue
                    
                    if any(kw == btn_text or kw in btn_text for kw in target_keywords):
                        # 排除某些可能混淆的按鈕 (例如包含 Agent 或 Chat 的開關)
                        if "Agent" in btn_text or "Chat" in btn_text:
                            continue

                        if btn_text in self.pending_buttons:
                            continue

                        print(f"🚨 Permission dialog detected: {btn_text}")
                        self.pending_buttons[btn_text] = btn
                        
                        keyboard = [
                            [
                                InlineKeyboardButton(f"✅ 同意: {btn_text}", callback_data=f"gui_permit_{btn_text}"),
                                InlineKeyboardButton("❌ 忽略", callback_data="gui_ignore")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"🛡️ **Antigravity 請求權限**\n偵測到按鈕：`{btn_text}`\n請點擊下方按鈕以對遠端進行操作：",
                            reply_markup=reply_markup,
                            parse_mode="Markdown"
                        )
                except:
                    continue
        except:
            pass

    def perform_click(self, btn_name):
        if btn_name in self.pending_buttons:
            try:
                btn = self.pending_buttons[btn_name]
                print(f"🖱️ Performing GUI click on: {btn_name}")
                win32gui.SendMessage(btn.top_level_parent().handle, 0x0050, 0, 0x04090409)
                btn.click_input()
                del self.pending_buttons[btn_name]
                return True
            except Exception as e:
                print(f"Click failed: {e}")
        return False

class GUIController:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.window_title = None

    def switch_to_english_input(self):
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SendMessage(hwnd, 0x0050, 0, 0x04090409)
        for _ in range(2):
            pyautogui.press('esc')
            time.sleep(0.05)
        print("⌨️ Forced English Layout + Cleared IME.")

    async def find_antigravity_window(self):
        titles = gw.getAllTitles()
        for t in titles:
            if "Antigravity" in t and "Visual Studio Code" not in t:
                if "antigravity-remote-bridge" in t and " - Antigravity" not in t:
                    continue
                return t
        return None

    async def run_prompt(self, prompt):
        try:
            target_title = await self.find_antigravity_window()
            if not target_title:
                await self.bot.send_message(chat_id=self.chat_id, text="❌ 找不到 IDE 視窗。")
                return False
            
            self.window_title = target_title
            windows = gw.getWindowsWithTitle(target_title)
            win = windows[0]
            if win.isMinimized: win.restore()
            
            for i in range(3):
                try: win.activate(); break
                except: await asyncio.sleep(1)
            
            await asyncio.sleep(1)
            self.switch_to_english_input()
            
            # 在按 Ctrl+L 前，嘗試觀察對話框是否已經打開 (捷徑：尋找特定文字)
            # 這裡我們為了保守起見，依然按下快捷鍵，但我們增加一點防護
            await self.bot.send_message(chat_id=self.chat_id, text="🎹 正在開啟 Agent 面板...")
            
            # 使用 Ctrl+L。如果發生「重複點擊」可能是因為快捷鍵送出太快或系統延遲
            # 我們嘗試確保視窗是真的有在焦點上
            win32gui.SetForegroundWindow(win._hWnd)
            
            # 嘗試先點擊一下視窗中央確保聚焦，但為了避免點到功能按鈕，點擊偏下方位置
            # pyautogui.click(win.left + 100, win.top + win.height - 100)
            
            pyautogui.hotkey('ctrl', 'l')
            await asyncio.sleep(1.5)
            
            # 再次 Esc 一次確保沒有選字窗卡住
            pyautogui.press('esc')
            
            await self.bot.send_message(chat_id=self.chat_id, text=f"⌨️ 正在輸入指令...")
            pyautogui.write(prompt, interval=0.01)
            await asyncio.sleep(0.5)
            pyautogui.press('enter')
            
            self.relay_monitor = PermissionRelayMonitor(self.bot, self.chat_id, target_title)
            await self.relay_monitor.start()
            
            return True

        except Exception as e:
            await self.bot.send_message(chat_id=self.chat_id, text=f"❌ GUI 操作失敗: {str(e)}")
            return False

    async def stop_monitor(self):
        if hasattr(self, 'relay_monitor'):
            await self.relay_monitor.stop()

    async def handle_callback(self, data):
        if data.startswith("gui_permit_"):
            btn_name = data.replace("gui_permit_", "")
            if hasattr(self, 'relay_monitor'):
                success = self.relay_monitor.perform_click(btn_name)
                return f"已點擊: {btn_name}" if success else "點擊失敗"
        return "已忽略"

    async def show_popup(self, text):
        func = lambda: pymsgbox.alert(text, title="TopGun Remote Bridge")
        await asyncio.get_event_loop().run_in_executor(None, func)

class TaskWatchdog:
    def __init__(self, bot, chat_id, docs_path):
        self.bot = bot
        self.chat_id = chat_id
        self.docs_path = docs_path

    async def wait_for_file(self, filename, gui_controller, timeout=300):
        target = os.path.join(self.docs_path, filename)
        start_time = time.time()
        await self.bot.send_message(chat_id=self.chat_id, text=f"👀 正在監控檔案生成: `{filename}`...")
        
        while time.time() - start_time < timeout:
            if os.path.exists(target):
                size = os.path.getsize(target)
                if size > 0:
                    await self.bot.send_message(
                        chat_id=self.chat_id, 
                        text=f"🔔 **偵測到檔案生成！**\n名稱: `{filename}`\n任務執行成功 ✅",
                        parse_mode="Markdown"
                    )
                    await gui_controller.stop_monitor()
                    return True
            await asyncio.sleep(5)
            
        await self.bot.send_message(chat_id=self.chat_id, text=f"⚠️ 等候逾時: `{filename}`。")
        await gui_controller.stop_monitor()
        return False

class AgentExecutor:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.gui_controller = GUIController(bot, chat_id)

    async def run(self, cmd, cwd, send_ask_func):
        prompt = cmd
        if 'chat "' in cmd:
            try: prompt = cmd.split('chat "')[1].rsplit('"', 1)[0]
            except: pass
        
        success = await self.gui_controller.run_prompt(prompt)
        
        if success:
            filename = None
            if "系統分析.md" in prompt: filename = "系統分析.md"
            elif "系統設計.md" in prompt: filename = "系統設計.md"
            elif "architecture.md" in prompt: filename = "architecture.md"
            
            if filename:
                docs_path = os.path.join(cwd, "docs")
                if not os.path.exists(docs_path): os.makedirs(docs_path, exist_ok=True)
                watchdog = TaskWatchdog(self.bot, self.chat_id, docs_path)
                asyncio.create_task(watchdog.wait_for_file(filename, self.gui_controller))
        else:
            await self.bot.send_message(chat_id=self.chat_id, text="❌ 觸發失敗。")

    async def handle_gui_callback(self, data):
        return await self.gui_controller.handle_callback(data)

    def send_input(self, char):
        pass
