from pywinauto import Application
import pygetwindow as gw

def dump_buttons():
    titles = gw.getAllTitles()
    target_title = None
    for t in titles:
        if "Antigravity" in t and "Visual Studio Code" not in t:
            if "antigravity-remote-bridge" in t and " - Antigravity" not in t:
                continue
            target_title = t
            break
    
    if not target_title:
        print("No Antigravity window found.")
        return

    print(f"Target: {target_title}")
    try:
        app = Application(backend="uia").connect(title=target_title, timeout=5)
        win = app.window(title=target_title)
        
        print("\n--- BUTTONS ---")
        buttons = win.descendants(control_type="Button")
        for btn in buttons:
            try:
                print(f"Text: '{btn.window_text()}', Class: {btn.class_name()}, Visible: {btn.is_visible()}, Enabled: {btn.is_enabled()}")
            except:
                pass
                
        print("\n--- ALL DESCENDANTS (Truncated) ---")
        # Just show first 50 to avoid too much spam
        for i, child in enumerate(win.descendants()):
            if i > 100: break
            try:
                print(f"{child.control_type()} | '{child.window_text()}'")
            except:
                pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_buttons()
