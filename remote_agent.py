import os
import json
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from core.infrastructure.system_ctrl import SystemController


# --- 讀取設定檔 ---
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print(f"❌ 找不到 {CONFIG_FILE}！請先建立並填入 TOKEN 與 ID。")
    exit()

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config.get("TOKEN")
AUTHORIZED_CHAT_ID = config.get("AUTHORIZED_CHAT_ID")
BASE_PROJECT_PATH = config.get("BASE_PROJECT_PATH", r"D:\project")

# 暫存使用者的當前專案狀態
user_context = {}


# --- 功能函式 ---
def get_project_list():
    try:
        # 自動掃描路徑下的資料夾
        return [
            d
            for d in os.listdir(BASE_PROJECT_PATH)
            if os.path.isdir(os.path.join(BASE_PROJECT_PATH, d))
        ]
    except Exception as e:
        print(f"掃描失敗: {e}")
        return []


def get_project_menu():
    projects = get_project_list()
    keyboard = []
    
    # 專案列表
    if projects:
        for p in projects:
            keyboard.append([InlineKeyboardButton(f"📁 {p}", callback_data=f"select_{p}")])
    
    # 系統控制按鈕
    is_locked = SystemController.is_screen_locked()
    status_icon = "🔒" if is_locked else "🔓"
    status_text = "解除鎖定" if is_locked else "鎖定系統"
    callback = "system_unlock" if is_locked else "system_lock"
    
    keyboard.append([InlineKeyboardButton(f"{status_icon} {status_text}", callback_data=callback)])
    
    return InlineKeyboardMarkup(keyboard)



def get_task_menu(proj_name):
    keyboard = [
        [
            InlineKeyboardButton("📊 總結進度", callback_data="task_summary"),
            InlineKeyboardButton("🏗️ 系統架構", callback_data="task_arch"),
        ],
        [InlineKeyboardButton("📂 檔案列表", callback_data="task_ls")],
        [
            InlineKeyboardButton("📝 修改文檔", callback_data="task_edit_doc"),
            InlineKeyboardButton("💻 修改 Code", callback_data="task_edit_code"),
        ],
        [
            InlineKeyboardButton(
                "🔍 文檔 -> Code TODO", callback_data="task_gap_doc2code"
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 Code -> 文檔 TODO", callback_data="task_gap_code2doc"
            )
        ],
        [InlineKeyboardButton("🛠️ 執行：TODO 改 Code", callback_data="task_sync_code")],
        [InlineKeyboardButton("🛠️ 執行：TODO 改文檔", callback_data="task_sync_doc")],
        [InlineKeyboardButton("🔙 返回專案選擇", callback_data="back_to_projects")],
    ]
    return InlineKeyboardMarkup(keyboard)


# --- 指令處理 ---


# /start 指令：啟動主選單
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    menu = get_project_menu()
    is_locked = SystemController.is_screen_locked()
    status_str = "🔒 **系統鎖定中**" if is_locked else "✅ **系統正常 (已解鎖)**"
    
    await update.message.reply_text(
        f"🚀 **TopGun 遠端系統已就緒**\n\n當前狀態：{status_str}\n\n請從下方選擇你要操作的專案或控制系統：",
        reply_markup=menu,
        parse_mode="Markdown",
    )



# /help 指令：操作說明
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    help_text = (
        "❓ **TopGun 遠端助手操作說明**\n\n"
        "1️⃣  輸入 `/start` 顯示所有專案資料夾。\n"
        "2️⃣  選擇專案後，點擊對應任務按鈕。\n"
        "3️⃣  Antigravity 會在後端執行，完成後會將日誌傳回手機。\n\n"
        "💡 *提示：任務執行中請稍候，大型分析可能需要 30-60 秒。*"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# 按鈕回調處理
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # 專案選擇邏輯
    if data.startswith("select_"):
        proj_name = data.split("_", 1)[1]
        user_context[user_id] = proj_name
        await query.edit_message_text(
            f"📍 **當前專案：{proj_name}**\n請選擇要執行的任務：",
            reply_markup=get_task_menu(proj_name),
            parse_mode="Markdown",
        )
        return

    # 返回邏輯
    if data == "back_to_projects":
        is_locked = SystemController.is_screen_locked()
        status_str = "🔒 **系統鎖定中**" if is_locked else "✅ **系統正常 (已解鎖)**"
        await query.edit_message_text(
            f"🚀 **當前狀態：{status_str}**\n請選擇專案或控制系統：", 
            reply_markup=get_project_menu(),
            parse_mode="Markdown"
        )
        return

    # 系統控制邏輯
    if data == "system_lock":
        await SystemController.lock_screen()
        await query.answer("🔒 系統已鎖定")
        # 重新整理選單
        await query.edit_message_text(
            "🚀 **系統已鎖定**\n請選擇操作：",
            reply_markup=get_project_menu(),
            parse_mode="Markdown"
        )
        return

    if data == "system_unlock":
        await SystemController.unlock_screen()
        await query.answer("🔓 已發送解除鎖定訊號 (請確認螢幕是否喚醒)")
        # 稍微延遲後重新整理狀態看是否成功 (雖然 is_screen_locked 在模擬按鍵後不一定立刻變，但試試看)
        import asyncio
        await asyncio.sleep(1)
        is_locked = SystemController.is_screen_locked()
        status_str = "🔒 **系統鎖定中**" if is_locked else "✅ **系統正常 (已解鎖)**"
        await query.edit_message_text(
            f"🚀 **當前狀態：{status_str}**\n請選擇操作：",
            reply_markup=get_project_menu(),
            parse_mode="Markdown"
        )
        return


    # 任務執行邏輯
    proj_name = user_context.get(user_id)
    if not proj_name:
        await query.message.reply_text("❌ 請先使用 /start 選擇專案。")
        return

    full_path = os.path.join(BASE_PROJECT_PATH, proj_name)

    tasks = {
        "task_summary": 'antigravity "總結昨日開發進度"',
        "task_arch": 'antigravity "讀取原始碼並在 document/architecture.md 生成架構圖"',
        "task_ls": 'antigravity "列出目錄結構，排除 node_modules"',
        "task_edit_doc": 'antigravity "讀取程式碼，修正 document/ 下不一致的文檔"',
        "task_edit_code": 'antigravity "根據需求，修改 src/ 下的程式碼"',
        "task_gap_doc2code": 'antigravity "比對文檔與程式碼，產出 code_todo.md"',
        "task_gap_code2doc": 'antigravity "比對程式碼與文檔，產出 doc_todo.md"',
        "task_sync_code": 'antigravity "讀取 code_todo.md，執行程式碼修改"',
        "task_sync_doc": 'antigravity "讀取 doc_todo.md，更新系統文檔"',
    }

    if data in tasks:
        status_msg = await query.message.reply_text(
            f"⏳ **正在執行：**\n`{tasks[data]}`", parse_mode="Markdown"
        )
        cmd = f'cd /d "{full_path}" && {tasks[data]}'

        try:
            # 執行指令
            process = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
            )
            output = process.stdout if process.stdout else process.stderr

            # 回傳結果，並將日誌用程式碼區塊包起來
            await status_msg.edit_text(
                f"✅ **任務完成！**\n\n**【執行日誌】**\n```text\n{output[:3500]}\n```",
                parse_mode="Markdown",
            )
        except Exception as e:
            await status_msg.edit_text(
                f"❌ **執行失敗**\n錯誤訊息：`{str(e)}`", parse_mode="Markdown"
            )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # 註冊指令
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # 註冊按鈕回調
    app.add_handler(CallbackQueryHandler(button_handler))

    print(f"🤖 遠端開發助手監聽中...")
    print(f"📁 專案根目錄: {BASE_PROJECT_PATH}")
    print(f"💡 請在 Telegram 中對機器人輸入 /start 或點擊 Menu 啟動")
    app.run_polling()
# python remote_agent.py
