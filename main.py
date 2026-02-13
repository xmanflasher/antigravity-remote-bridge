import json
import os
from core.presentation.bot_manager import BotManager

def main():
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"❌ 找不到 {config_file}！")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    bot_manager = BotManager(config)
    bot_manager.run()

if __name__ == "__main__":
    main()
