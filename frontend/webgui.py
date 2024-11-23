import streamlit as st
import doVote
import time
from streamlit_autorefresh import st_autorefresh  # 確保已安裝 streamlit_autorefresh


class Page:
    """基礎頁面類，所有頁面繼承此類"""

    def __init__(self, app):
        self.app = app  # 保存主應用物件的引用

    def show(self):
        """顯示頁面的方法，需由子類實現"""
        raise NotImplementedError("子類必須實現 show 方法")


class LoginPage(Page):
    """登入頁面"""

    def show(self):
        # 切換按鈕放在頂部
        if st.button("切換到註冊", key="switch_to_register"):
            self.app.set_page("register")
            st.rerun()

        st.title("登入頁面")

        # 輸入框
        username = st.text_input("帳號", key="username_login")
        password = st.text_input("密碼", type="password", key="password_login")

        # 登入按鈕
        if st.button("登入"):
            if username and password:  # 驗證是否輸入帳號和密碼
                # 調用 doVote.login_user API
                login_result = doVote.login_user(username, password)
                if login_result and isinstance(login_result, dict):
                    if "idToken" in login_result:
                        st.success("登入成功！")
                        self.app.set_user_id(login_result["idToken"])  # 保存 idToken 到主應用
                        self.app.set_page("vote")  # 切換到投票頁面
                        st.rerun()  # 確保頁面刷新
                    else:
                        st.error(f"登入失敗: {login_result.get('error', '未知錯誤')}")
                else:
                    st.error("登入失敗: 無法解析伺服器回應")
            else:
                st.error("請輸入帳號和密碼")


class RegisterPage(Page):
    """註冊頁面"""

    def show(self):
        # 切換按鈕放在頂部
        if st.button("切換到登入", key="switch_to_login"):
            self.app.set_page("login")
            st.rerun()

        st.title("註冊頁面")

        # 輸入框
        username = st.text_input("帳號", key="username_register")
        password = st.text_input("密碼", type="password", key="password_register")
        confirm_password = st.text_input("確認密碼", type="password", key="confirm_password_register")

        # 註冊按鈕
        if st.button("註冊"):
            if username and password and confirm_password:  # 簡單檢查
                if password == confirm_password:
                    # 調用 doVote.register_user API
                    register_result = doVote.register_user(username, password)
                    if "success" in register_result:
                        st.success("註冊成功！請切換到登入頁面")
                    else:
                        st.error(f"註冊失敗: {register_result.get('error', '未知錯誤')}")
                else:
                    st.error("密碼與確認密碼不一致")
            else:
                st.error("請輸入帳號、密碼和確認密碼")


class VotePage(Page):
    """投票頁面"""

    def show(self):
        st.title("投票頁面")
        st.write("請為你喜歡的候選人投票！")

        # 確認用戶是否已登入
        if self.app.user_id:
            # 可選：顯示用戶 ID
            # st.write(f"登入用戶 ID: {self.app.user_id}")
            pass
        else:
            st.error("未登入，請返回登入頁面")
            self.app.set_page("login")
            st.rerun()

        # 獲取候選人列表，使用 cache_data 緩存
        candidates = VotePage.get_candidates()

        # 顯示候選人
        for candidate in candidates:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"No.{candidate['rank']} {candidate['name']} - {candidate['votes']} 票")
            with col2:
                if st.button("投票", key=f"vote_{candidate['vote_id']}"):
                    try:
                        # 進行投票操作
                        doVote.vote(self.app.user_id, candidate['vote_id'], 'string')

                        st.success("已成功投票！")

                        # 清除候選人緩存並重新獲取候選人列表
                        VotePage.clear_candidates_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"投票失敗: {e}")

        # 登出按鈕
        if st.button("登出", key="logout"):
            self.app.clear_user_id()  # 清除登入 ID
            self.app.set_page("login")
            st.rerun()

    @staticmethod
    @st.cache_data(ttl=10)
    def get_candidates():
        return doVote.get_candidates()

    @staticmethod
    def clear_candidates_cache():
        VotePage.get_candidates.clear()


class StreamlitApp:
    """主應用類，負責頁面切換和管理"""

    def __init__(self):
        # 初始化頁面狀態
        if "current_page" not in st.session_state:
            st.session_state.current_page = "login"  # 預設頁面為登入頁面
        if "user_id" not in st.session_state:
            st.session_state.user_id = None  # 預設無登入用戶
        self.pages = {
            "login": LoginPage(self),
            "register": RegisterPage(self),
            "vote": VotePage(self),
        }

    @property
    def current_page(self):
        return st.session_state.current_page

    @current_page.setter
    def current_page(self, page_name):
        st.session_state.current_page = page_name

    @property
    def user_id(self):
        return st.session_state.user_id

    @user_id.setter
    def user_id(self, user_id):
        st.session_state.user_id = user_id

    def set_page(self, page_name):
        self.current_page = page_name

    def set_user_id(self, user_id):
        self.user_id = user_id

    def clear_user_id(self):
        self.user_id = None

    def run(self):
        """主程式入口，根據頁面狀態顯示對應頁面"""
        page = self.current_page
        if page in self.pages:
            self.pages[page].show()
        else:
            st.error("未知頁面，請重新登入！")
            self.set_page("login")
            st.rerun()


# 啟動應用
if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
