import sys
import os
import time

# Add core to path
sys.path.append(os.getcwd())

from core.infrastructure.system_ctrl import SystemController

async def test_lock_cycle():
    print("--- Windows Lock Cycle Debug ---")
    
    # Init
    sys_ctrl = SystemController()
    
    # 1. Initial State
    is_locked = sys_ctrl.is_screen_locked()
    print(f"[!] Initial state: {'LOCKED' if is_locked else 'UNLOCKED'}")
    
    if not is_locked:
        print("[>] Locking screen in 2 seconds...")
        await asyncio.sleep(2)
        await sys_ctrl.lock_screen()
        await asyncio.sleep(2)
        is_locked = sys_ctrl.is_screen_locked()
        print(f"[!] State after locking: {'LOCKED' if is_locked else 'UNLOCKED'}")
    
    if is_locked:
        print("\n[>] Starting Unlock Sequence...")
        
        # Step A: Wake with Mouse
        print("[A] Wiggling mouse...")
        import pyautogui
        pyautogui.moveRel(10, 10)
        await asyncio.sleep(0.5)
        pyautogui.moveRel(-10, -10)
        await asyncio.sleep(1)
        
        # Step B: ESC
        print("[B] Pressing ESC...")
        pyautogui.press('esc')
        await asyncio.sleep(1)
        
        # Step C: Enter (to dismiss wallpaper)
        print("[C] Pressing ENTER...")
        pyautogui.press('enter')
        await asyncio.sleep(2) # Give it more time for animation
        
        # Step D: Space (to ensure focus)
        print("[D] Pressing SPACE...")
        pyautogui.press('space')
        await asyncio.sleep(1)
        
        # Final Check
        is_locked = sys_ctrl.is_screen_locked()
        print(f"\n[!] Final state: {'LOCKED' if is_locked else 'UNLOCKED'}")
        
        if is_locked:
            print("[❌] Unlock cycle failed to restore 'UNLOCKED' state.")
        else:
            print("[✅] Unlock cycle successfully restored 'UNLOCKED' state!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_lock_cycle())

