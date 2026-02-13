import os
import telebot
import subprocess

bot = telebot.TeleBot("7025811335:AAFbjqQhjqyvAePsJlOqDVtRRLOK52oftxA")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    prompt = message.text
    chat_id = message.chat.id

    # 指向你的 .cmd 檔案
    # 注意：在 Windows 中，呼叫 .cmd 有時需要透過 cmd.exe /c
    cmd_path = r"D:\Antigravity\bin\antigravity.cmd"
    cwd_path = r"D:\project\TopGun"

    bot.send_message(chat_id, f"🔨 正在強行啟動視窗...\n任務: {prompt}")

    try:
        # 這次我們使用 Windows 的 'start' 指令
        # 這樣會像你在 CMD 手動輸入一樣，跳出一個獨立的視窗
        full_command = f'start "" "{cmd_path}" chat "{prompt}"'

        print(f"執行指令: {full_command}")

        # 使用 os.system 或 subprocess.Popen 啟動一個完全脫離 Python 的進程
        subprocess.Popen(full_command, shell=True, cwd=cwd_path)

        bot.send_message(chat_id, "✅ 啟動指令已送出！請確認電腦是否有新視窗跳出。")

    except Exception as e:
        bot.send_message(chat_id, f"❌ 啟動失敗: {str(e)}")


print("🤖 視窗強制開啟版啟動...")
bot.polling()
