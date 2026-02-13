from pywinauto import Desktop

def list_windows():
    windows = Desktop(backend="uia").windows()
    print(f"{'Title':<60} | {'Class':<30}")
    print("-" * 95)
    for w in windows:
        try:
            title = w.window_text()
            if title:
                print(f"{title:<60} | {w.class_name():<30}")
        except:
            continue

if __name__ == "__main__":
    list_windows()
