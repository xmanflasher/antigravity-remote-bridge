import pyautogui
import asyncio
import time
import pygetwindow as gw

class GUIController:
    def __init__(self, system_controller):
        self.sys_ctrl = system_controller

    async def _ensure_visible(self, element, status_callback=None):
        """
        確保元素可見，若不可見則嘗試捲動。
        """
        try:
            if not element.is_offscreen():
                return True
            
            if status_callback: await status_callback("🖱️ 元素在畫面外，嘗試捲動面板...")
            
            # 嘗試使用 Scroll Pattern
            from pywinauto import patterns
            if element.is_pattern_supported(patterns.ScrollItemPattern):
                element.set_focus()
                element.scroll_into_view()
                time.sleep(0.5)
                return not element.is_offscreen()
            
            # 備援方案：模擬滾輪
            element.set_focus()
            for _ in range(5):
                pyautogui.scroll(-300) # 往下捲動
                time.sleep(0.2)
                if not element.is_offscreen():
                    return True
            return False
        except:
            return False

    async def open_agent_panel(self, window_title, status_callback=None):
        from pywinauto import Application
        import win32gui
        
        if status_callback: await status_callback("🔍 偵測 Agent 面板狀態...")
        
        loop = asyncio.get_event_loop()
        def _check_and_open(loop):
            try:
                hwnd = win32gui.FindWindow(None, window_title)
                if not hwnd: return False
                
                win32gui.SetForegroundWindow(hwnd)
                # 使用 uia 模式連接
                app = Application(backend="uia").connect(handle=hwnd, timeout=2)
                main_win = app.window(handle=hwnd)
                
                # 1. 嘗試快速判斷 (Ctrl+Alt+B 可能是快速切換或聚焦)
                # 先按 Ctrl+Alt+B 加快「呼喚」Agent 的速度
                if status_callback: asyncio.run_coroutine_threadsafe(status_callback("🎹 呼喚 Agent (Ctrl+Alt+B)..."), loop)
                pyautogui.hotkey('ctrl', 'alt', 'b')
                time.sleep(0.8)

                # 2. 檢查面板是否已開啟
                panel_open = False
                # 標題關鍵字，通常編輯框會有這些標題
                indicators = ["Ask anything", "Message Agent", "Chat"]
                for indicator in indicators:
                    try:
                        # 稍微放寬 depth, 但限制 control_type 為 Edit
                        if main_win.child_window(title_re=f".*{indicator}.*", control_type="Edit", depth=15).exists(timeout=0.5):
                            panel_open = True
                            break
                    except: continue
                
                if panel_open:
                    if status_callback: asyncio.run_coroutine_threadsafe(status_callback("✅ Agent 面板已就緒。"), loop)
                    return True

                # 3. 備援方案：Ctrl+L (傳統開啟方式)
                if status_callback: asyncio.run_coroutine_threadsafe(status_callback("🎹 嘗試 Ctrl+L 開啟面板..."), loop)
                pyautogui.press('esc')
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(1.5)
                
                # 最終確認
                for indicator in indicators:
                    try:
                        if main_win.child_window(title_re=f".*{indicator}.*", control_type="Edit", depth=15).exists(timeout=0.8):
                            return True
                    except: continue
                
                return False # 真的找不到
            except Exception as e:
                if status_callback: asyncio.run_coroutine_threadsafe(status_callback(f"⚠️ 偵測異常: {str(e)[:30]}"), loop)
                return False

        return await asyncio.to_thread(_check_and_open, loop)

    async def enter_prompt(self, prompt, window_title, status_callback=None):
        import pyperclip
        from pywinauto import Application
        import win32gui
        
        if status_callback: await status_callback(f"📋 注入指令中...")

        loop = asyncio.get_event_loop()
        def _uia_input(loop):
            try:
                hwnd = win32gui.FindWindow(None, window_title)
                if not hwnd: return "WIN_NOT_FOUND"
                
                win32gui.SetForegroundWindow(hwnd)
                app = Application(backend="uia").connect(handle=hwnd, timeout=2)
                main_win = app.window(handle=hwnd)
                
                # 尋找輸入框 (Edit 型態) - 擴大搜尋範圍
                target_box = None
                # 嘗試組合：標題關鍵字 + 控制項類型
                indicators = ["Ask anything", "Message Agent", "Chat", "Input", "Search"]
                
                if status_callback: asyncio.run_coroutine_threadsafe(status_callback("🧐 正在搜尋輸入框..."), loop)
                
                for name in indicators:
                    try:
                        # 嘗試不同 depth 與標題組合
                        box = main_win.child_window(title_re=f".*{name}.*", control_type="Edit", depth=15)
                        if box.exists(timeout=0.2):
                            target_box = box
                            if status_callback: asyncio.run_coroutine_threadsafe(status_callback(f"🎯 找到輸入框: {name}"), loop)
                            break
                    except: continue

                if not target_box:
                    # 嘗試找所有 Edit 類型並分析位置
                    try:
                        edits = main_win.descendants(control_type="Edit")
                        visible_edits = [e for e in edits if e.is_visible()]
                        if visible_edits:
                            win_rect = main_win.rectangle()
                            win_height = win_rect.height()
                            
                            # 按照 Y 座標排序
                            visible_edits.sort(key=lambda x: x.rectangle().top)
                            
                            # 判斷情境：
                            # 如果只有一個主要 Edit 且在中間 -> 可能是初始狀態
                            # 如果有多個，選取最下方的一個 -> 正常對話狀態
                            # 此處我們優先找「寬度較大」且「看起來像輸入框」的
                            best_box = None
                            for e in reversed(visible_edits):
                                r = e.rectangle()
                                # 輸入框通常寬度至少佔寬度的一半
                                if r.width() > win_rect.width() * 0.4:
                                    best_box = e
                                    # 如果在最下方，這就是對了
                                    if r.top > win_rect.top + win_height * 0.7:
                                        if status_callback: asyncio.run_coroutine_threadsafe(status_callback("📥 偵測到對話框在底部。"), loop)
                                        break
                                    # 如果在中間，先記著，繼續看有沒有更下方的
                                    if r.top > win_rect.top + win_height * 0.3:
                                        if status_callback: asyncio.run_coroutine_threadsafe(status_callback("� 偵測到初始對話框 (居中)。"), loop)
                                        # 不 break, 可能還有更下面的
                            
                            target_box = best_box or visible_edits[-1]
                    except: pass
                
                if target_box:
                    try:
                        target_box.set_focus()
                        time.sleep(0.1)
                        target_box.click_input()
                    except:
                        # 備援：直接點選中心
                        rect = target_box.rectangle()
                        pyautogui.click(rect.mid_point().x, rect.mid_point().y)
                    time.sleep(0.5)
                else:
                    if status_callback: asyncio.run_coroutine_threadsafe(status_callback("⚠️ 找不到精確輸入框，使用座標備援"), loop)
                    rect = main_win.rectangle()
                    # 考慮 Agent 可能在右側或底部
                    # 嘗試點選視窗右下方區域
                    cx = rect.left + rect.width() - 150
                    cy = rect.top + rect.height() - 80 
                    pyautogui.click(cx, cy)
                    time.sleep(0.5)
                
                 # 清理並輸入 - 增加保險
                pyperclip.copy(prompt)
                
                # 強制切換英文輸入法 (再次確保)
                # 這部分在 trigger_agent 已經做過一次，此處為雙重保險
                
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('backspace')
                time.sleep(0.2)
                
                # 模擬貼上
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.8) # 等候文字渲染
                
                # 再次確認輸入框是否有內容 (可選，但對於 UIA 可能有用)
                # 這裡直接送出
                pyautogui.press('enter')
                
                return "SUCCESS"
            except Exception as e:
                import traceback
                print(f"DEBUG: {traceback.format_exc()}")
                return str(e)

        result = await asyncio.to_thread(_uia_input, loop)
        if result == "SUCCESS":
            if status_callback: await status_callback("✅ 指令已送出。")
            return True
        else:
            if status_callback: await status_callback(f"❌ 失敗: {result}")
            return False

    async def trigger_agent(self, prompt, window_title, status_callback=None):
        # 注意：此處 prompt 填入前已經由 ensure_environment_ready 處理過視窗定位與面板
        # 但為了保險，這裡再次呼叫一次 enter_prompt
        # 這裡的 window_title 是 caller 應該已經搜尋到的
        try:
            return await asyncio.wait_for(self.enter_prompt(prompt, window_title, status_callback), timeout=30)
        except:
            return False

    async def check_for_pending_buttons(self, window_title, status_callback=None):
        """
        情境式按鈕檢查：
        1. 偵測可見按鈕 (Allow, Run, Accept)
        2. 若偵測到問題字眼 (如 Run command?) 但無可見按鈕，嘗試捲動
        """
        from pywinauto import Application
        import win32gui
        
        loop = asyncio.get_event_loop()
        def _check(loop):
            try:
                hwnd = win32gui.FindWindow(None, window_title)
                if not hwnd: return []
                
                app = Application(backend="uia").connect(handle=hwnd, timeout=1.5)
                main_win = app.window(handle=hwnd)
                
                permit_keywords = ["Allow Once", "Allow This Conversation", "Allow", "Accept All", "Run", "全部接受", "允許", "Reject", "Keep", "拒絕", "保留"]
                # 偵測是否有正在詢問的問題區
                question_keywords = ["Run command?", "Allow command?", "Execute?", "確定執行?"]
                
                def _scan_btns():
                    # 擴大搜尋深度與類型
                    # 有些 Webview 按鈕可能沒被標記為 Button，我們也找 Text 和 MenuItem
                    found = []
                    # 1. 直接用 child_window 找關鍵字 (最快)
                    for kw in permit_keywords:
                        try:
                            # 嘗試找包含關鍵字的元素
                            btn = main_win.child_window(title_re=f".*{kw}.*", depth=18)
                            if btn.exists(timeout=0.05):
                                txt = btn.window_text()
                                if txt and len(txt) < 50:
                                    if not any(x in txt for x in ["Chat", "Agent", "Stop", "Minimize", "Maximize", "Close", "Panel"]):
                                        found.append(txt)
                        except: continue
                    
                    if found: return list(set(found))

                    # 2. 深度遍歷 (較準確但慢些)
                    # 增加到 depth=18 確保抓到 Webview 內部
                    btns = main_win.descendants(depth=18)
                    for element in btns:
                        try:
                            # 限制為 Button, MenuItem, Text, Hyperlink
                            ctrl_type = element.control_type()
                            if ctrl_type not in ["Button", "MenuItem", "Text", "Hyperlink"]: continue
                            
                            text = element.window_text()
                            if not text or len(text) > 40: continue
                            
                            # 排除常見介面按鈕
                            if any(x in text for x in ["Chat", "Agent", "Stop", "Minimize", "Maximize", "Close", "Panel"]): continue
                            
                            # 關鍵字比對 (不分大小寫且支援部分匹配)
                            if any(kw.lower() in text.lower() for kw in permit_keywords):
                                found.append(text)
                        except: continue
                    return list(set(found))

                # 1. 偵測可見按鈕
                visible_btns = _scan_btns()
                if visible_btns:
                    return visible_btns
                
                # 2. 偵測是否有問題字眼但按鈕沒出現（可能在下方）
                has_question = False
                texts = main_win.descendants(control_type="Text", depth=15)
                for t in texts:
                    try:
                        val = t.window_text()
                        if any(q in val for q in question_keywords):
                            has_question = True
                            break
                    except: continue
                
                if has_question:
                    if status_callback: asyncio.run_coroutine_threadsafe(status_callback("🖱️ 偵測到指令請求但按鈕不可見，嘗試向下捲動..."), loop)
                    # 嘗試捲動面板
                    win32gui.SetForegroundWindow(hwnd)
                    # 點擊右側 Agent 區域確保焦點
                    rect = main_win.rectangle()
                    pyautogui.click(rect.left + rect.width() - 50, rect.top + rect.height() // 2)
                    for _ in range(3):
                        pyautogui.scroll(-500)
                        time.sleep(0.3)
                    
                    # 捲動後再次掃描
                    return _scan_btns()
                
                return []
            except Exception as e:
                print(f"DEBUG: check_for_pending_buttons error: {e}")
                return []

        result = await asyncio.to_thread(_check, loop)
        if result:
            if status_callback: await status_callback(f"🛡️ 偵測到阻塞按鈕: {', '.join(result)}")
        return result

    async def ensure_environment_ready(self, proj_path, status_callback=None):
        """
        一站式環境檢查：視窗 -> Snap -> Agent 面板 -> 檢查按鈕 -> 輸入框
        """
        import os
        proj_name = os.path.basename(proj_path)
        
        if status_callback: await status_callback(f"🚀 開始環境檢查：專案 `{proj_name}`")
        
        # 1. 搜尋視窗
        window_title = await self.sys_ctrl.find_antigravity_window(target_project=proj_name)
        if not window_title:
             if status_callback: await status_callback("❌ 找不到對應的 IDE 視窗。")
             return False, None
             
        # 2. 啟動/激活並 Snap
        if not await self.sys_ctrl.activate_window(window_title):
            return False, None
        await self.sys_ctrl.snap_window(window_title, side="left")
        
        # 3. 確保 Agent 面板開啟
        if not await self.open_agent_panel(window_title, status_callback):
             if status_callback: await status_callback("⚠️ 無法確保 Agent 面板已開啟。")
             # 繼續嘗試，不一定失敗
             
        # 4. 強制切換英文輸入法
        await self.sys_ctrl.switch_to_english_input()
        
        # 5. 檢查是否有阻塞按鈕
        pending_buttons = await self.check_for_pending_buttons(window_title, status_callback)
        if pending_buttons:
            if status_callback: await status_callback(f"🛡️ 發現等候中按鈕，中斷指令填入以求安全。")
            return False, window_title

        return True, window_title

    async def trigger_agent(self, prompt, window_title, status_callback=None):
        # 這裡的 trigger_agent 保留，但現在通常由 execute_task 先呼叫 ensure_environment_ready
        # 為了相容性，這裡可以封裝
        if status_callback: await status_callback("📋 準備注入指令...")
        return await self.enter_prompt(prompt, window_title, status_callback)
