from pywinauto import Application
import sys

def dump_controls(window_title):
    try:
        # 使用更精確的標題與類名
        app = Application(backend="uia").connect(title=window_title, class_name="Chrome_WidgetWin_1", timeout=10)
        window = app.window(title=window_title)
        
        print(f"Found window. Starting dump...")
        with open("gui_dump.txt", "w", encoding="utf-8") as f:
            sys.stdout = f
            window.print_control_identifiers()
            sys.stdout = sys.__stdout__
        
        print(f"Dump completed to gui_dump.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 從之前的清單中看到的精確標題
    dump_controls("TopGun - Antigravity")
