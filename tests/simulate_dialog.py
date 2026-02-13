import tkinter as tk
from tkinter import messagebox

def simulate():
    root = tk.Tk()
    root.title("Antigravity Simulation Dialog")
    root.geometry("400x200")
    
    label = tk.Label(root, text="🛡️ 模擬 Antigravity 權限請求", font=("Arial", 12))
    label.pack(pady=20)
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    
    # Matching keywords from PermissionRelayMonitor
    btn1 = tk.Button(btn_frame, text="Allow Once", command=lambda: print("Clicked: Allow Once"))
    btn1.pack(side=tk.LEFT, padx=5)
    
    btn2 = tk.Button(btn_frame, text="Allow This Conversation", command=lambda: print("Clicked: Allow This Conversation"))
    btn2.pack(side=tk.LEFT, padx=5)
    
    btn3 = tk.Button(btn_frame, text="Deny", command=lambda: print("Clicked: Deny"))
    btn3.pack(side=tk.LEFT, padx=5)

    print("🚀 Simulation Dialog is running. Title: 'Antigravity Simulation Dialog'")
    root.mainloop()

if __name__ == "__main__":
    simulate()
