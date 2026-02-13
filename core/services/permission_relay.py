import asyncio
from pywinauto import Application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import win32gui

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
        import win32gui
        try:
            # Connect to main window to get handle
            hwnd = win32gui.FindWindow(None, self.window_title)
            if not hwnd: return
            
            # Find all renderer widgets (where content lives)
            # This is much faster than global UIA scan
            renderers = []
            def callback(h, _):
                if win32gui.GetClassName(h) == "Chrome_RenderWidgetHostHWND":
                    renderers.append(h)
                return True
            win32gui.EnumChildWindows(hwnd, callback, None)
            
            permit_keywords = ["Allow Once", "Allow This Conversation", "Allow", "Accept All", "Run", "全部接受", "允許"]
            deny_keywords = ["Deny", "Cancel", "Ignore", "拒絕", "取消"]
            
            found_permit = []
            found_deny = []
            
            for rhwnd in renderers:
                try:
                    # Scan each renderer widget with shallow UIA
                    app = Application(backend="uia").connect(handle=rhwnd, timeout=0.5)
                    root = app.window(handle=rhwnd)
                    
                    # We use a depth limit to stay fast
                    # Most permission buttons in chat are 3-5 levels down from the renderer root
                    btns = root.descendants(control_type="Button", depth=6)
                    
                    for btn in btns:
                        try:
                            text = btn.window_text()
                            if not text or len(text) > 40: continue
                            if not btn.is_visible(): continue
                            
                            is_permit = any(kw == text or (len(kw) > 3 and kw in text) for kw in permit_keywords)
                            is_deny = any(kw == text or (len(kw) > 3 and kw in text) for kw in deny_keywords)

                            if is_permit:
                                if any(x in text for x in ["Chat", "Agent", "Stop", "Minimize", "Close"]): continue
                                found_permit.append((text, btn))
                            elif is_deny:
                                if any(x in text for x in ["Chat", "Agent", "Close"]): continue
                                found_deny.append((text, btn))
                        except: continue
                except: continue

            if not found_permit and not found_deny:
                return

            # Signature logic to avoid duplicate spamming
            sig = "-".join(sorted([t for t, b in found_permit + found_deny]))
            if sig in self.pending_buttons:
                # Still check if we need to refresh (optional)
                return

            print(f"🚨 Permission dialog detected via renderer scan: {sig}")
            
            dialog_id = f"dlg_{int(asyncio.get_event_loop().time())}"
            self.pending_buttons[sig] = {
                "id": dialog_id,
                "buttons": {text: btn for text, btn in found_permit + found_deny}
            }

            keyboard = []
            row = []
            for text, _ in found_permit:
                row.append(InlineKeyboardButton(f"✅ {text}", callback_data=f"gui_permit_{text}"))
                if len(row) >= 2:
                    keyboard.append(row)
                    row = []
            if row: keyboard.append(row)
            
            deny_row = []
            for text, _ in found_deny:
                deny_row.append(InlineKeyboardButton(f"❌ {text}", callback_data=f"gui_permit_{text}"))
            if deny_row: keyboard.append(deny_row)

            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"🛡️ **Antigravity 權限請求**\n偵測到權端操作申請，請選擇：",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception:
            pass

    def perform_click(self, btn_name):
        import win32con
        import time
        
        # Scan all pending dialogs for this button name
        for sig, data in list(self.pending_buttons.items()): # Iterate over a copy to allow deletion
            if btn_name in data["buttons"]:
                try:
                    btn = data["buttons"][btn_name]
                    print(f"🖱️ Clicking GUI Button: {btn_name}")
                    
                    # Bring parent to foreground aggressively
                    parent = btn.top_level_parent()
                    handle = parent.handle
                    
                    # 1. Restore if minimized
                    if win32gui.IsIconic(handle):
                        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
                    
                    # 2. Force to front
                    win32gui.ShowWindow(handle, win32con.SW_SHOW)
                    win32gui.SetForegroundWindow(handle)
                    
                    # 3. Wait for UI to stabilize
                    time.sleep(0.5)
                    
                    # 4. Perform click
                    btn.click_input()
                    
                    # Cleanup this specific dialog set
                    del self.pending_buttons[sig]
                    return True
                except Exception as e:
                    print(f"❌ Click failed for {btn_name}: {e}")
        return False
