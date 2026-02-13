import unittest
import asyncio
from core.permission_relay import PermissionRelayMonitor

class MockButton:
    def __init__(self, name):
        self.name = name
        self.handle = 1234
    def window_text(self):
        return self.name
    def is_visible(self):
        return True
    def is_enabled(self):
        return True
    def top_level_parent(self):
        return self
    def click_input(self):
        print(f"Clicked: {self.name}")

class MockBot:
    async def send_message(self, chat_id, text, reply_markup, parse_mode):
        pass

class TestRelayLogic(unittest.TestCase):
    def test_grouping_logic(self):
        monitor = PermissionRelayMonitor(MockBot(), "123", "Title")
        
        # Simulating finding buttons
        found_permit = [("Allow Once", MockButton("Allow Once")), ("Allow", MockButton("Allow"))]
        found_deny = [("Deny", MockButton("Deny"))]
        
        # Test signature generation
        sig = "-".join(sorted([t for t, b in found_permit + found_deny]))
        self.assertIn("Allow-Allow Once-Deny", sig)
        
        # Test internal state storage logic (partial manual check of monitor behavior)
        dialog_id = "dlg_test"
        monitor.pending_buttons[sig] = {
            "id": dialog_id,
            "buttons": {text: btn for text, btn in found_permit + found_deny}
        }
        
        self.assertTrue(monitor.perform_click("Allow Once"))
        self.assertNotIn(sig, monitor.pending_buttons)

if __name__ == "__main__":
    unittest.main()
