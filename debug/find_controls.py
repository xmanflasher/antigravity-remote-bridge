from pywinauto import Application

def find_chat_controls():
    try:
        title = "TopGun - Antigravity"
        print(f"Connecting to: {title}")
        app = Application(backend="uia").connect(title=title, class_name="Chrome_WidgetWin_1", timeout=5)
        window = app.window(title=title)
        
        print("Searching for Edit and Button elements...")
        # 搜尋所有的 Edit 控制項 (通常輸入框是 Edit 或 Document)
        edits = window.descendants(control_type="Edit")
        print(f"Found {len(edits)} Edit controls.")
        for i, e in enumerate(edits):
            try:
                print(f"Edit {i}: Name='{e.window_text()}', ID='{e.element_info.automation_id}'")
            except: pass

        docs = window.descendants(control_type="Document")
        print(f"Found {len(docs)} Document controls.")
        for i, d in enumerate(docs):
            try:
                 print(f"Doc {i}: Name='{d.window_text()}', ID='{d.element_info.automation_id}'")
            except: pass

        btns = window.descendants(control_type="Button")
        print(f"Found {len(btns)} Buttons.")
        for i, b in enumerate(btns):
            try:
                # 只印出有名字的按鈕
                t = b.window_text()
                if t:
                    print(f"Button {i}: Name='{t}'")
            except: pass

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_chat_controls()
