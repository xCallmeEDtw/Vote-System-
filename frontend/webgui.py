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
        st.title("投票箱列表")
        st.write("請選擇一個投票箱進入！")

        # 確認用戶是否已登入
        if self.app.user_id:
            pass
        else:
            st.error("未登入，請返回登入頁面")
            self.app.set_page("login")
            st.rerun()

        # 獲取投票箱列表
        candidates = doVote.get_candidates()

        # 顯示投票箱
        for candidate in candidates:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"投票箱名稱: {candidate['name']} - 總票數: {candidate['votes']}")
            with col2:
                if st.button("進入", key=f"enter_{candidate['vote_id']}"):
                    self.app.current_vote_box = candidate['vote_id']  # 設置當前投票箱 ID
                    self.app.set_page("vote_box")  # 跳轉到投票箱詳細頁
                    st.rerun()

        # 登出按鈕
        if st.button("登出", key="logout"):
            self.app.clear_user_id()  # 清除登入 ID
            self.app.set_page("login")
            st.rerun()



class VoteBoxPage(Page):
    """投票箱詳細頁面"""

    def show(self):
        st.title("投票選項")
        st.write("請為您支持的選項投票！")

        # 確認用戶是否已登入
        if self.app.user_id:
            pass
        else:
            st.error("未登入，請返回登入頁面")
            self.app.set_page("login")
            st.rerun()

        # 確認當前是否有選擇的投票箱
        if not self.app.current_vote_box:
            st.error("未選擇投票箱，請返回選擇投票箱")
            self.app.set_page("vote")
            st.rerun()

        # 自動刷新機制
        refresh_interval = 10  # 設定自動刷新間隔（秒）
        count = st_autorefresh(interval=refresh_interval * 1000, key="autorefresh_vote_box")

        # 獲取投票箱選項
        try:
            options = doVote.get_vote_options(self.app.current_vote_box)
        except Exception as e:
            st.error(f"無法獲取投票選項: {e}")
            return

        # 顯示選項
        for option in options:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"選項: {option['name']} - 得票數: {option['votes']}")
            with col2:
                if st.button("投票", key=f"vote_{option['name']}"):
                    try:
                        # 調用 doVote.vote API 進行投票
                        doVote.vote(self.app.user_id, self.app.current_vote_box, option['name'])
                        st.success(f"已成功為 {option['name']} 投票！")
                        st.rerun()  # 手動刷新頁面
                    except Exception as e:
                        st.error(f"投票失敗: {e}")

        # 返回投票箱列表
        if st.button("返回投票箱列表"):
            self.app.set_page("vote")
            st.rerun()




class StreamlitApp:
    """主應用類，負責頁面切換和管理"""

    def __init__(self):
        if "current_page" not in st.session_state:
            st.session_state.current_page = "login"
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "current_vote_box" not in st.session_state:
            st.session_state.current_vote_box = None
        self.pages = {
            "login": LoginPage(self),
            "register": RegisterPage(self),
            "vote": VotePage(self),
            "vote_box": VoteBoxPage(self),
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

    @property
    def current_vote_box(self):
        return st.session_state.current_vote_box

    @current_vote_box.setter
    def current_vote_box(self, vote_box_id):
        st.session_state.current_vote_box = vote_box_id

    def set_page(self, page_name):
        self.current_page = page_name

    def set_user_id(self, user_id):
        self.user_id = user_id

    def clear_user_id(self):
        self.user_id = None

    def set_current_vote_box(self, vote_box_id):
        self.current_vote_box = vote_box_id

    def clear_current_vote_box(self):
        self.current_vote_box = None

    def run(self):
        page = self.current_page
        if page in self.pages:
            self.pages[page].show()
        else:
            st.error("未知頁面，請重新登入！")
            self.set_page("login")
            st.rerun()


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
