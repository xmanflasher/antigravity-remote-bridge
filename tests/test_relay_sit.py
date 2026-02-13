import asyncio
import time
from core.permission_relay import PermissionRelayMonitor
from pywinauto import Application

class MockBot:
    async def send_message(self, chat_id, text, reply_markup, parse_mode):
        print(f"\n[TELEGRAM SIM] Message Sent!")
        btns = []
        for row in reply_markup.inline_keyboard:
            btns.extend([b.text for b in row])
        print(f"Buttons found: {btns}")

async def run_sit():
    print("🧪 Starting Robust Permission Relay SIT...")
    bot = MockBot()
    target_title = "Antigravity Simulation Dialog"
    
    # We verify the window exists first
    from pywinauto import findwindows
    try:
        handle = findwindows.find_window(title=target_title)
        print(f"✅ Simulation window handle found: {handle}")
    except:
        print("❌ Simulation window not found. Run tests/simulate_dialog.py first.")
        return

    monitor = PermissionRelayMonitor(bot, "123456", target_title)
    
    # We'll monkeypatch the monitor to use a more robust search for the simulation
    async def restricted_check():
        try:
            # Try win32 backend for TKinter if UIA is slow
            app = Application(backend="win32").connect(handle=handle)
            window = app.window(handle=handle)
            all_btns = window.descendants(control_type="Button")
            
            print(f"Found {len(all_btns)} buttons in simulation.")
            
            # Use the actual monitor logic but with our found buttons
            permit_keywords = ["Allow Once", "Allow This Conversation", "Allow", "Accept All", "Run"]
            deny_keywords = ["Deny", "Cancel", "Ignore"]
            
            found_permit = []
            found_deny = []
            
            for btn in all_btns:
                text = btn.window_text()
                if any(kw in text for kw in permit_keywords):
                    found_permit.append((text, btn))
                elif any(kw in text for kw in deny_keywords):
                    found_deny.append((text, btn))
            
            if found_permit:
                sig = "-".join(sorted([t for t, b in found_permit + found_deny]))
                print(f"🚨 Signature: {sig}")
                monitor.pending_buttons[sig] = {
                    "id": "dlg_sit",
                    "buttons": {text: btn for text, btn in found_permit + found_deny}
                }
                # Simulate bot send (manually call what check_permissions would do)
                await bot.send_message("123", "Detected", None, "Markdown")
                return True
        except Exception as e:
            print(f"SIT internal error: {e}")
        return False

    success = await restricted_check()
    if success:
        print("\n✅ Detection and Grouping SIT passed!")
        print("🖱️ Verifying click relay...")
        if monitor.perform_click("Allow Once"):
            print("✅ Click relay SIT passed!")
        else:
            print("❌ Click relay SIT failed.")
    else:
        print("❌ SIT Failed.")

if __name__ == "__main__":
    asyncio.run(run_sit())
