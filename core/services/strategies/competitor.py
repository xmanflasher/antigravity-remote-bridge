import os
from core.services.strategies.base import TaskStrategy
from core.tasks import detect_framework

class CompetitorAnalysisTask(TaskStrategy):
    def get_name(self) -> str:
        return "競品分析"

    async def pre_work(self, context, status_update_func=None) -> bool:
        """
        防呆與自動化：確保 ref_docs/ 存在並判斷其內容
        """
        if status_update_func: await status_update_func("🔍 準備競品分析：檢查參考文件...")
        
        proj_path = context.config.get("CURRENT_PROJ_PATH") 
        if not proj_path:
            return True
            
        ref_path = os.path.join(proj_path, "ref_docs")
        
        # 1. 判斷有無 ref_docs/，無則創建
        if not os.path.exists(ref_path):
            os.makedirs(ref_path)
            if status_update_func: await status_update_func("📁 已建立 ref_docs/ 目錄。")
            
        # 2. 判斷 ref_docs 之下有無文件或圖檔
        files = [f for f in os.listdir(ref_path) if os.path.isfile(os.path.join(ref_path, f))]
        self.has_files = len(files) > 0
        
        if not self.has_files:
            if status_update_func: await status_update_func("💡 偵測到無參考文件，將執行專案優化/改善計畫。")
        else:
            if status_update_func: await status_update_func(f"📑 偵測到 {len(files)} 份參考文件/圖檔，準備執行競品分析。")
            
        return True

    def get_prompt(self, proj_path: str, custom_prompt: str = None) -> str:
        framework = detect_framework(proj_path)
        SCOPE_ADVICE = f"\n[優化建議] 專案偵測為 {framework}。請優先分析 src/ 目錄及主要設定檔。"
        
        if not getattr(self, "has_files", True):
            # 無文件：要求提出優化或改善計畫
            return (
                f"由於目前 ref_docs/ 中無任何參考文件，請根據當前專案的功能與結構進行深度分析，"
                f"並提出至少三個具體的『優化或改善計畫』。請將結果詳細寫入 docs/improvement_plan.md。{SCOPE_ADVICE}"
            )
        
        # 有文件：要求做競品分析
        return (
            f"請分析 ref_docs/ 中的競品文檔或圖檔，提取其核心功能亮點與技術優勢，"
            f"並與當前專案進行對比，生成一份完整的 competitor_analysis.md 並放在 docs 目錄。{SCOPE_ADVICE}"
        )

    def get_watch_file(self) -> str:
        if not getattr(self, "has_files", True):
            return "improvement_plan.md"
        return "competitor_analysis.md"
