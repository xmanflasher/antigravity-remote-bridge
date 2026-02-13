import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from core.presentation.bot_handler import get_project_menu, get_main_menu, get_doc_menu, get_coding_menu, get_browser_menu, get_busy_menu
from core.infrastructure.system_ctrl import SystemController
from core.infrastructure.gui_ctrl import GUIController
from core.services.permission_relay import PermissionRelayMonitor
from core.services.task_service import TaskService
from core.services.strategies.general import ANALYSIS_TASK, DESIGN_TASK, SUMMARY_TASK, CODING_TASK, INPUT_REQ_TASK
from core.services.strategies.competitor import CompetitorAnalysisTask

class BotManager:
    def __init__(self, config):
        self.config = config
        self.state_file = "bridge_state.json"
        self.user_context = self._load_state()
        self.executor_context = {} 
        self.sys_ctrl = SystemController()
        self.gui_ctrl = GUIController(self.sys_ctrl)
        self.task_service = TaskService(config, self.sys_ctrl, self.gui_ctrl)
        
        # 註冊策略
        self.task_service.register_strategy("task_sys_analysis", ANALYSIS_TASK)
        self.task_service.register_strategy("task_sys_design", DESIGN_TASK)
        self.task_service.register_strategy("task_summary", SUMMARY_TASK)
        self.task_service.register_strategy("task_coding", CODING_TASK)
        self.task_service.register_strategy("task_input_req", INPUT_REQ_TASK)
        self.task_service.register_strategy("task_competitor", CompetitorAnalysisTask())
        self.task_service.register_strategy("task_todo_suggest", ANALYSIS_TASK)
        self.task_service.register_strategy("task_sync_code", CODING_TASK)

        self.relay_monitor = None
        self.current_task = None
        self.status_text = "閒置中 (Idle)"
        self.anchor_messages = {} # user_id -> message_id

    def _load_state(self):
        import json
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return {int(k): v for k, v in json.load(f).items()}
            except: pass
        return {}

    def _save_state(self):
        import json
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_context, f, ensure_ascii=False, indent=2)
        except: pass

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != self.config["AUTHORIZED_CHAT_ID"]:
            return
        user_id = update.effective_user.id
        proj = self.user_context.get(user_id)
        
        text, reply_markup = get_main_menu(proj)
        
        if self.current_task and not self.current_task.done():
            _, busy_markup = get_busy_menu(proj)
            text = f"⏳ **系統忙碌中**\n目前正在執行：`{self.status_text}`"
            reply_markup = busy_markup

        msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        self.anchor_messages[user_id] = msg.message_id

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data, user_id = query.data, query.from_user.id
        proj = self.user_context.get(user_id)

        if data == "main_menu":
            await query.answer()
            text, markup = get_main_menu(proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data == "back_prev":
            await query.answer()
            text, markup = get_main_menu(proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data == "menu_docs":
            await query.answer()
            text, markup = get_doc_menu(proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data == "menu_coding":
            await query.answer()
            text, markup = get_coding_menu(proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data == "menu_browser":
            await query.answer()
            text, markup = get_browser_menu(proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data == "warn_no_proj":
            await query.answer("⚠️ 請先在「專案列表」中選擇專案資料夾。", show_alert=True)

        elif data == "bot_restart":
            await query.answer()
            await query.edit_message_text("♻️ **正在重啟監控程序...**")
            if self.relay_monitor:
                await self.relay_monitor.stop()
            import sys
            os.execv(sys.executable, ['python'] + sys.argv)

        elif data.startswith("select_"):
            await query.answer()
            proj = data.split("_", 1)[1]
            self.user_context[user_id] = proj
            self._save_state()
            path = os.path.join(self.config["BASE_PROJECT_PATH"], proj)
            
            _, busy_markup = get_busy_menu(proj)
            await query.edit_message_text(
                f"📍 **當前專案：{proj}**\n正在啟動 Antigravity 並分析環境...",
                reply_markup=busy_markup,
                parse_mode="Markdown",
            )
            
            self.sys_ctrl.launch_antigravity(path)
            
            async def delayed_prep():
                await asyncio.sleep(4)
                title = await self.sys_ctrl.find_antigravity_window(target_project=proj)
                if title:
                    self.sys_ctrl.snap_window(title, side="left")
                try:
                    prep_text, prep_markup = get_main_menu(proj)
                    await query.edit_message_text(
                        f"✅ 專案 `{proj}` 已就緒。\n{prep_text}",
                        reply_markup=prep_markup,
                        parse_mode="Markdown"
                    )
                except: pass
            
            asyncio.create_task(delayed_prep())

        elif data == "back_to_projects":
            await query.answer()
            text, markup = get_project_menu(self.config["BASE_PROJECT_PATH"], proj)
            await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

        elif data.startswith("gui_permit_"):
            await query.answer()
            btn_name = data.replace("gui_permit_", "")
            if self.relay_monitor:
                success = await self.gui_ctrl.click_element(self.relay_monitor.window_title, btn_name)
                msg = f"已點擊: {btn_name}" if success else "點擊失敗"
                await query.edit_message_text(f"🔘 {msg}")

        elif data == "gui_ignore":
            await query.answer()
            await query.edit_message_text("🔘 已忽略權限請求")

        elif data == "gui_interrupt":
            await query.answer()
            if self.current_task:
                self.current_task.cancel()
                self.current_task = None
            if self.relay_monitor:
                await self.relay_monitor.stop()
            self.status_text = "閒置中 (Interrupted)"
            text, markup = get_main_menu(proj)
            await query.edit_message_text(f"❌ 指令已中斷。\n{text}", reply_markup=markup, parse_mode="Markdown")

        elif data == "gui_status":
            await query.answer()
            status_info = f"🔍 **當前狀態**：{self.status_text}"
            if proj: status_info += f"\n📍 **當前專案**：`{proj}`"
            
            if self.relay_monitor and self.relay_monitor.running:
                status_info += f"\n🛡️ **權限監控中**：目標 `{self.relay_monitor.window_title}`"
                asyncio.create_task(self.relay_monitor.check_permissions())
            
            await query.answer(status_info.replace("**", "").replace("`", ""), show_alert=True)

        elif data in ["browse_docs", "browse_ref_docs"]:
            if not proj:
                await query.answer("⚠️ 請先選擇專案。", show_alert=True)
                return
            
            sub_dir = "docs" if data == "browse_docs" else "ref_docs"
            dir_path = os.path.join(self.config["BASE_PROJECT_PATH"], proj, sub_dir)
            
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
            files = []
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                
            keyboard_btns = []
            for f in files:
                keyboard_btns.append([InlineKeyboardButton(f"📄 {f}", callback_data=f"file_{sub_dir}_{f}")])
            
            from core.presentation.bot_handler import get_layout
            layout_text, reply_markup = get_layout(f"瀏覽 {sub_dir}", proj, keyboard_btns, show_back=True)
            await query.edit_message_text(f"📁 **請選擇文件：**\n{layout_text}", reply_markup=reply_markup, parse_mode="Markdown")

        elif data.startswith("file_"):
            parts = data.split("_", 2)
            sub_dir, filename = parts[1], parts[2]
            file_path = os.path.join(self.config["BASE_PROJECT_PATH"], proj, sub_dir, filename)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=self.config["AUTHORIZED_CHAT_ID"], document=f, caption=f"📄 {filename}")
            else:
                await query.answer("❌ 找不到該文件。", show_alert=True)

        elif data.startswith("task_"):
            await query.answer(f"🚀 已排程任務: {data}", show_alert=False)
            if self.current_task and not self.current_task.done():
                await query.answer("⚠️ 系統忙碌中，請先中斷或等候完成。", show_alert=True)
                return

            if not proj:
                await query.answer("⚠️ 請先選擇專案資料夾後再下指令。", show_alert=True)
                return

            path = os.path.join(self.config["BASE_PROJECT_PATH"], proj)
            self.task_service.config["CURRENT_PROJ_PATH"] = path 
            
            text, busy_markup = get_busy_menu(proj)
            # 轉義 data 中的底線避免 Markdown 解析錯誤
            safe_data = data.replace("_", "\\_")
            status_msg_edit = await query.edit_message_text(
                f"⏳ **發送任務：{safe_data}**\n{text}", 
                reply_markup=busy_markup,
                parse_mode="Markdown"
            )

            async def status_cb(text_in):
                self.status_text = text_in
                _, inner_busy_markup = get_busy_menu(proj)
                try: await status_msg_edit.edit_text(f"⏳ **執行中...**\n{text_in}", reply_markup=inner_busy_markup, parse_mode="Markdown")
                except: pass

            async def run_task_logic():
                try:
                    result = await self.task_service.execute_task(data, path, context.bot, self.config["AUTHORIZED_CHAT_ID"], status_cb)
                    if result:
                        _, window_title, watch_file = result
                        if self.relay_monitor:
                            await self.relay_monitor.stop()
                        self.relay_monitor = PermissionRelayMonitor(context.bot, self.config["AUTHORIZED_CHAT_ID"], window_title)
                        await self.relay_monitor.start()
                        
                        if watch_file:
                            docs_path = os.path.join(path, "docs")
                            await self.watch_file(context.bot, watch_file, docs_path, status_msg_edit, proj)
                        else:
                            ok_text, ok_markup = get_main_menu(proj)
                            await status_msg_edit.edit_text(f"✅ 指令已送出，監控中...\n{ok_text}", reply_markup=ok_markup, parse_mode="Markdown")
                except asyncio.CancelledError:
                    pass
                finally:
                    self.current_task = None
                    self.status_text = "閒置中 (Idle)"

            self.current_task = asyncio.create_task(run_task_logic())

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != self.config["AUTHORIZED_CHAT_ID"]:
            return
        
        if self.current_task and not self.current_task.done():
            await update.message.reply_text("⚠️ 系統忙碌中，請先中斷或等候完成。")
            return

        user_id = update.effective_user.id
        proj = self.user_context.get(user_id)
        if not proj:
            await update.message.reply_text("⚠️ 請先選擇專案資料夾後再下指令。")
            return

        prompt = update.message.text
        _, busy_markup = get_busy_menu(proj)
        status_msg = await update.message.reply_text(
            f"🚀 **發送自定義內容**\n正在處理中...", 
            reply_markup=busy_markup,
            parse_mode="Markdown"
        )

        async def status_cb(text):
            self.status_text = text
            _, inner_busy_markup = get_busy_menu(proj)
            try: await status_msg.edit_text(f"🚀 **執行中...**\n{text}", reply_markup=inner_busy_markup, parse_mode="Markdown")
            except: pass

        async def run_custom_task():
            try:
                # 執行就緒檢查
                path = os.path.join(self.config["BASE_PROJECT_PATH"], proj)
                ready, window_title = await self.gui_ctrl.ensure_environment_ready(path, status_cb)
                if not ready:
                    if window_title:
                         # 有按鈕阻塞
                         return
                    else:
                        mt_text, mt_markup = get_main_menu(proj)
                        await status_msg.edit_text(f"❌ 無法就緒環境切換。\n{mt_text}", reply_markup=mt_markup, parse_mode="Markdown")
                        return

                success = await self.gui_ctrl.trigger_agent(prompt, window_title, status_cb)
                if success:
                    if self.relay_monitor:
                        await self.relay_monitor.stop()
                    self.relay_monitor = PermissionRelayMonitor(context.bot, self.config["AUTHORIZED_CHAT_ID"], window_title)
                    await self.relay_monitor.start()
                    
                    ok_text, ok_markup = get_main_menu(proj)
                    await status_msg.edit_text(f"✅ 指令已送出，監控中...\n{ok_text}", reply_markup=ok_markup, parse_mode="Markdown")
                else:
                    fail_text, fail_markup = get_main_menu(proj)
                    await status_msg.edit_text(f"❌ 執行失敗或超時。\n{fail_text}", reply_markup=fail_markup, parse_mode="Markdown")
            except asyncio.CancelledError:
                pass
            finally:
                self.current_task = None
                self.status_text = "閒置中 (Idle)"

        self.current_task = asyncio.create_task(run_custom_task())

    async def watch_file(self, bot, filename, docs_path, status_msg, proj_name, timeout=300):
        target = os.path.join(docs_path, filename)
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if await asyncio.to_thread(os.path.exists, target) and await asyncio.to_thread(os.path.getsize, target) > 0:
                await bot.send_message(
                    chat_id=self.config["AUTHORIZED_CHAT_ID"], 
                    text=f"🔔 **偵測到檔案生成！**\n名稱: `{filename}`\n任務執行成功 ✅",
                    parse_mode="Markdown"
                )
                res_text, res_markup = get_main_menu(proj_name)
                await status_msg.edit_text(f"✅ 任務完成：`{filename}`\n{res_text}", reply_markup=res_markup, parse_mode="Markdown")
                if self.relay_monitor:
                    await self.relay_monitor.stop()
                return True
            await asyncio.sleep(5)
            
        res_text, res_markup = get_main_menu(proj_name)
        await status_msg.edit_text(f"⚠️ 等候逾時: `{filename}`。\n{res_text}", reply_markup=res_markup, parse_mode="Markdown")
        if self.relay_monitor:
            await self.relay_monitor.stop()
        return False

    def run(self):
        app = ApplicationBuilder().token(self.config["TOKEN"]).build()
        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text))
        print("🤖 遠端控制台已啟動...")
        app.run_polling()
