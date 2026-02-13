import asyncio
import os
from core.services.strategies.base import TaskStrategy

class TaskService:
    """
    負責協調任務執行、生命週期管理與防呆機制
    """
    def __init__(self, config, sys_ctrl, gui_ctrl):
        self.config = config
        self.sys_ctrl = sys_ctrl
        self.gui_ctrl = gui_ctrl
        self.strategies = {}
        self.current_task = None
        self.status_text = "閒置中 (Idle)"

    def register_strategy(self, key: str, strategy: TaskStrategy):
        self.strategies[key] = strategy

    async def execute_task(self, task_key: str, proj_path: str, bot, chat_id, status_update_func):
        """
        核心執行邏輯：防呆 -> 前置作業 -> 啟動 IDE -> 監控
        """
        strategy = self.strategies.get(task_key)
        if not strategy:
            raise ValueError(f"找不到任務策略: {task_key}")

        # 1. 前置作業 (由策略決定，如檢查目錄)
        can_proceed = await strategy.pre_work(self, status_update_func)
        if not can_proceed:
            return False
            
        # 2. 環境就緒檢查 (視窗、面板、按鈕阻塞等)
        ready, window_title = await self.gui_ctrl.ensure_environment_ready(proj_path, status_update_func)
        if not ready:
            if window_title is None:
                return False # 視窗找不到，由裡面 handle 訊息
            else:
                return False # 有按鈕阻塞或其他問題

        # 3. 準備 Prompt
        prompt = strategy.get_prompt(proj_path)
        
        # 4. 觸發 Agent
        success = await self.gui_ctrl.trigger_agent(prompt, window_title, status_update_func)
        if not success:
            await status_update_func("❌ 指令注入失敗。")
            return False

        return True, window_title, strategy.get_watch_file()

    def cancel_task(self):
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
        self.status_text = "閒置中 (Interrupted)"
