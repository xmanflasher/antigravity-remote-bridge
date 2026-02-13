import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_layout(func_name, proj_name, middle_buttons, show_back=True, show_exit=True):
    """
    通用版面配置 (Markdown + InlineKeyboard):
    
    [LABEL] 
    💎 功能｜func_name
    🎯 專案｜proj_name
    ------------------
    { middle_buttons }
    ------------------
    [導覽區]
    """
    # 建立訊息文字 (Markdown Label)
    proj_display = f"🎯 專案｜`{proj_name}`" if proj_name else "❌ 專案｜`未選擇`"
    text = (
        f"💎 **功能**｜#{func_name}\n"
        f"{proj_display}\n"
        f"────────────────"
    )
    
    # 建立按鈕
    keyboard = [
        [
            InlineKeyboardButton("🔍 偵測狀態", callback_data="gui_status"),
            InlineKeyboardButton("♻️ 監控重啟", callback_data="bot_restart"),
            InlineKeyboardButton("❌ 中斷程序", callback_data="gui_interrupt"),
        ],
        # 動態區分隔線 (使用網底視覺效果)
        [InlineKeyboardButton("▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", callback_data="none")],
    ]
    
    # Middle (Dynamic)
    keyboard.extend(middle_buttons)
    
    keyboard.append([InlineKeyboardButton("▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", callback_data="none")])
    
    # Footer Navigation
    footer_row = []
    if show_back:
        footer_row.append(InlineKeyboardButton("🔙 返回上層", callback_data="back_prev"))
    if show_exit:
        footer_row.append(InlineKeyboardButton("🏠 回主選單", callback_data="main_menu"))
    
    if footer_row:
        keyboard.append(footer_row)
        
    return text, InlineKeyboardMarkup(keyboard)

def get_main_menu(proj_name=None):
    has_proj = proj_name is not None
    def btn_text(text, active): return text if active else f"🔘 {text} (未選擇)"

    middle = [
        [InlineKeyboardButton("📂 專案列表 (切換專案)", callback_data="back_to_projects")],
        [
            InlineKeyboardButton(btn_text("📑 Documentation", has_proj), callback_data="menu_docs" if has_proj else "warn_no_proj"),
            InlineKeyboardButton(btn_text("💻 Coding", has_proj), callback_data="menu_coding" if has_proj else "warn_no_proj"),
        ],
        [InlineKeyboardButton(btn_text("📄 文件瀏覽", has_proj), callback_data="menu_browser" if has_proj else "warn_no_proj")]
    ]
    return get_layout("主選單", proj_name, middle, show_back=False, show_exit=False)

def get_project_menu(base_path, proj_name=None):
    projects = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    middle = [[InlineKeyboardButton(f"📁 {p}", callback_data=f"select_{p}")] for p in projects]
    return get_layout("專案選擇", proj_name, middle, show_back=False, show_exit=True)

def get_doc_menu(proj_name):
    middle = [
        [
            InlineKeyboardButton("🔍 系統分析", callback_data="task_sys_analysis"),
            InlineKeyboardButton("📐 系統設計", callback_data="task_sys_design"),
        ],
        [
            InlineKeyboardButton("📊 競品分析", callback_data="task_competitor"),
            InlineKeyboardButton("📈 總結進度", callback_data="task_summary"),
        ],
        [InlineKeyboardButton("💡 TODO 建議", callback_data="task_todo_suggest")]
    ]
    return get_layout("Documentation", proj_name, middle)

def get_coding_menu(proj_name):
    middle = [
        [InlineKeyboardButton("📥 輸入需求", callback_data="task_input_req")],
        [InlineKeyboardButton("🛠️ 執行 TODO", callback_data="task_sync_code")]
    ]
    return get_layout("Coding", proj_name, middle)

def get_browser_menu(proj_name):
    middle = [
        [InlineKeyboardButton("📂 docs (選擇 docs/)", callback_data="browse_docs")],
        [InlineKeyboardButton("📂 ref_docs (選擇 ref_docs/)", callback_data="browse_ref_docs")]
    ]
    return get_layout("文件瀏覽", proj_name, middle)

def get_busy_menu(proj_name):
    middle = [[InlineKeyboardButton("⏳ 任務執行中，請稍候...", callback_data="none")]]
    return get_layout("執行中", proj_name, middle, show_back=False)
