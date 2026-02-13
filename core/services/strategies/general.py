from core.services.strategies.base import TaskStrategy
from core.tasks import detect_framework

class GeneralTaskStrategy(TaskStrategy):
    def __init__(self, name, template, watch_file=None):
        self.name = name
        self.template = template
        self.watch_file = watch_file

    def get_name(self) -> str:
        return self.name

    def get_prompt(self, proj_path: str, custom_prompt: str = None) -> str:
        framework = detect_framework(proj_path)
        SCOPE_ADVICE = f"\n[優化建議] 專案偵測為 {framework}。請優先分析 src/ 目錄及主要設定檔。"
        
        if custom_prompt:
            return f"{custom_prompt}{SCOPE_ADVICE}"
            
        return f"{self.template}{SCOPE_ADVICE}"

    def get_watch_file(self) -> str:
        return self.watch_file

# 定義具體任務範本
ANALYSIS_TASK = GeneralTaskStrategy("系統分析", "請進行系統分析，生成『系統分析.md』並放在 docs 目錄下", "系統分析.md")
DESIGN_TASK = GeneralTaskStrategy("系統設計", "請進行系統設計，生成『系統設計.md』並放在 docs 目錄下", "系統設計.md")
SUMMARY_TASK = GeneralTaskStrategy("總結進度", "請總結進度並更新 docs/progress.md (比較當前進度與系統設計)", "progress.md")
CODING_TASK = GeneralTaskStrategy("執行編碼", "根據 todo_list.md 或文檔中的建議，執行對應的程式碼修改")
INPUT_REQ_TASK = GeneralTaskStrategy("輸入需求", "接收並分析使用者的新需求，準備更新文檔或程式碼")
