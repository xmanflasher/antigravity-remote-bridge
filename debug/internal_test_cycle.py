import time
import asyncio
from core.infrastructure.system_ctrl import SystemController

async def internal_test():
    print("--- Internal Lock/Unlock Test ---")
    
    print("Step 0: Checking initial state...")
    locked = SystemController.is_screen_locked()
    print(f"Initial State: {'LOCKED' if locked else 'UNLOCKED'}")
    
    if locked:
        print("System is already locked. Please unlock it manually before starting the test.")
        return

    print("Step 1: Locking screen in 5 seconds...")
    time.sleep(5)
    await SystemController.lock_screen()
    
    # Give it time to lock
    time.sleep(3)
    locked = SystemController.is_screen_locked()
    print(f"State after lock: {'LOCKED' if locked else 'UNLOCKED'}")
    
    if not locked:
        print("FAILED: System did not lock.")
        return

    print("Step 2: Waiting 5 seconds, then attempting UNLOCK...")
    time.sleep(5)
    
    success = await SystemController.unlock_screen()
    print(f"Unlock sequence return value: {success}")
    
    # Final check
    time.sleep(5)
    final_locked = SystemController.is_screen_locked()
    print(f"Final State: {'LOCKED' if final_locked else 'UNLOCKED'}")
    
    if not final_locked:
        print("SUCCESS: System was successfully unlocked!")
    else:
        print("FAILED: System is still locked.")

if __name__ == "__main__":
    asyncio.run(internal_test())
