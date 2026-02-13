import os


def normalize_path(path, style="posix"):
    """
    路徑適配器：確保 Windows 與 AI 對路徑的認知一致。
    """
    if not path:
        return ""
    abs_path = os.path.abspath(path)
    if style == "posix":
        return abs_path.replace("\\", "/")
    return abs_path.replace("/", "\\")


def get_agent_prompt(proj_path):
    """
    生成標準化的 Agent 提示語，解決之前 Markdown 解析崩潰的問題。
    """
    safe_path = normalize_path(proj_path, style="posix")
    proj_name = os.path.basename(safe_path.strip("/"))

    # 使用單行指令，避免換行符號導致 Antigravity 介面異常
    return (
        f"環境:{safe_path}。專案:{proj_name}。"
        "指令:1.先list_dir('.')確認檔案 2.調用工具修改內容 3.等待授權。"
    )
