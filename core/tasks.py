import os

def detect_framework(proj_path):
    """偵測專案的語言與框架"""
    try:
        files = os.listdir(proj_path)
        if "pom.xml" in files:
            return "Java/Maven (focus on pom.xml, src/)"
        if "package.json" in files:
            return "Node.js (focus on package.json, src/)"
        if "requirements.txt" in files or "pyproject.toml" in files:
            return "Python (focus on requirements.txt, src/)"
        if "pubspec.yaml" in files:
            return "Flutter (focus on lib/, pubspec.yaml)"
        if "AndroidManifest.xml" in files or "build.gradle" in files:
            return "Android (focus on src/, build.gradle)"
        if "Info.plist" in files:
            return "iOS (focus on Runner/, Info.plist)"
        if "go.mod" in files:
            return "Go (focus on go.mod, src/)"
    except:
        pass
    return "Unknown (focus on src/ and config files)"

def get_antigravity_cmd(task_key, proj_path, custom_prompt=None):
    # 偵測框架以優化掃描範圍
    framework = detect_framework(proj_path)
    
    # 優化提示詞：告知 Agent 縮小範圍，避免掃描 node_modules, .git 等
    SCOPE_ADVICE = f"\n[優化建議] 專案偵測為 {framework}。請優先分析 src/ 目錄及主要設定檔，避免全面掃描以節省資源。"

    AGENT_PREFIX = "請執行任務："

    if task_key == "custom" and custom_prompt:
        return f'{custom_prompt}{SCOPE_ADVICE}'

    templates = {
        "task_summary": f'{AGENT_PREFIX} 總結進度並更新 docs/progress.md (比較當前進度與系統設計)',
        "task_competitor": f'{AGENT_PREFIX} 分析 ref_docs/ 中的競品文檔，並提取核心功能亮點',
        "task_todo_suggest": f'{AGENT_PREFIX} 根據當前的系統分析與設計，對比競品分析結果，列出尚未實作或建議強化的 TODO 清單',
        "task_input_req": f'{AGENT_PREFIX} 接收並分析使用者的新需求，準備更新文檔或程式碼',
        "task_sync_code": f'{AGENT_PREFIX} 根據 todo_list.md 或文檔中的建議，執行對應的程式碼修改',
        "task_arch": f'{AGENT_PREFIX} 生成 architecture.md 圖表',
        "task_ls": f'list_dir "."',
        "task_sys_analysis": '請進行系統分析，生成系統分析.md 並放在 docs 目錄下',
        "task_sys_design": '請進行系統設計，生成系統設計.md 並放在 docs 目錄下',
    }

    cmd = templates.get(task_key, '請分析此專案')
    return f"{cmd}{SCOPE_ADVICE}"