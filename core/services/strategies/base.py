import abc

class TaskStrategy(abc.ABC):
    """
    任務策略抽象基底類別
    """
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """回傳任務名稱"""
        pass

    @abc.abstractmethod
    def get_prompt(self, proj_path: str, custom_prompt: str = None) -> str:
        """生成任務 Prompt"""
        pass

    @abc.abstractmethod
    def get_watch_file(self) -> str:
        """回傳此任務生成的目標檔案名稱 (若無則回傳 None)"""
        pass

    async def pre_work(self, context, status_update_func=None) -> bool:
        """
        執行前置作業 (例如建立目錄、巡檢格式)
        回傳 True 表示可繼續執行，False 表示中斷
        """
        return True
