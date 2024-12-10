# streamlit run .\webgui.py
import streamlit as st
import doVote
import time
from streamlit_autorefresh import st_autorefresh  # 確保已安裝 streamlit_autorefresh
from streamlit_modal import Modal  # 確保已安裝 streamlit-modal 套件

st.markdown(
    """
    <style>
    .stButton button {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .stTitle {
        color: #4CAF50;
        font-family: 'Arial Black', sans-serif;
    }
    """
    ,
    unsafe_allow_html=True
)

class Page:
    """基礎頁面類，所有頁面繼承此類"""

    def __init__(self, app):
        self.app = app  # 保存主應用物件的引用

    def show(self):
        """顯示頁面的方法，需由子類實現"""
        raise NotImplementedError("Need to implement show method.")


class LoginPage(Page):
    """登入頁面"""

    def show(self):
        # 切換按鈕放在頂部
        if st.button("register an account", key="switch_to_register"):
            self.app.set_page("register")
            st.rerun()

        
        st.markdown('<h1 class="stTitle">Enter your identity</h1>', unsafe_allow_html=True)
        st.subheader("Not registered yet?")
        st.text("Click the 'Register an account' button above to register.")

        # 輸入框
        username = st.text_input("Account", key="username_login")
        password = st.text_input("Password", type="password", key="password_login")

        # 登入按鈕
        if st.button("sign in"):
            if username and password:  # 驗證是否輸入帳號和密碼
                # 調用 doVote.login_user API
                login_result = doVote.login_user(username, password)
                if login_result and isinstance(login_result, dict):
                    if "idToken" in login_result:
                        st.success("Welcome, voter!")
                        self.app.set_user_id(login_result["idToken"])  # 保存 idToken 到主應用
                        self.app.set_page("vote")  # 切換到投票頁面
                        st.rerun()  # 確保頁面刷新
                    else:
                        st.error(f"Sign in failed: {login_result.get('error', 'Unknown error')}")
                else:
                    st.error("Sign in failed: Unable to parse the server response")
            else:
                st.error("Enter your account and password.")

class RegisterPage(Page):
    """註冊頁面"""

    def show(self):
        # 切換按鈕放在頂部
        if st.button("Back to sign in page", key="switch_to_login"):
            self.app.set_page("login")
            st.rerun()

        st.markdown('<h1 class="stTitle">Create a new identity</h1>', unsafe_allow_html=True)
        st.subheader("Enter your email in the account field.")

        # 輸入框
        username = st.text_input("Account", key="username_register")
        password = st.text_input("Password", type="password", key="password_register")
        confirm_password = st.text_input("Confirm your password", type="password", key="confirm_password_register")

        # 註冊按鈕
        if st.button("create"):
            if username and password and confirm_password:  # 簡單檢查
                if password == confirm_password:
                    # 調用 doVote.register_user API
                    register_result = doVote.register_user(username, password)
                    if "success" in register_result:
                        st.success("Welcome, user! Please switch to the login page.")
                    else:
                        st.error(f"Registration failed: {register_result.get('error', 'Unknown error')}")
                else:
                    st.error("Password and confirm password do not match.")
            else:
                st.error("Enter your email, password, and confirm your password.")


class VotePage(Page):
    """投票頁面"""

    def __init__(self, app):
        super().__init__(app)

    def show(self):
        # 確認用戶是否已登入
        if self.app.user_id:
            pass
        else:
            st.error("Not logged in, please return to the login page.")
            self.app.set_page("login")
            st.rerun()

        # 獲取投票箱列表
        candidates = doVote.get_candidates()

        st.markdown('<h1 class="stTitle">Choose a topic to participate in</h1>', unsafe_allow_html=True)
        st.subheader("...or create your own topic.")

        # 顯示新增投票箱按鈕
        if st.button("Create new topic", key="add_vote"):
            st.session_state.show_add_vote_form = True  # 顯示表單

        # 顯示新增投票箱表單
        if st.session_state.get('show_add_vote_form', False):
            self.show_add_vote_form()

        st.markdown("---")
        st.subheader("Voting Topics")

        # 使用下拉選單選擇候選投票箱
        selected_candidate_name = st.selectbox("Select a topic", [candidate['name'] for candidate in candidates])

        # 尋找選中的投票箱
        selected_candidate = next((c for c in candidates if c['name'] == selected_candidate_name), None)

        if selected_candidate:
            if st.button("Vote", key=f"enter_{selected_candidate['vote_id']}"):
                # 設置當前投票箱並跳轉
                self.app.current_vote_box = selected_candidate['vote_id']
                self.app.current_vote_name = selected_candidate['name']
                self.app.set_page("vote_box")
                st.rerun()


        
        st.markdown("Note: Each participant has 1 vote for 1 topic.")

        # 顯示所有投票箱列表
        for candidate in candidates:
            st.markdown(f"- **{candidate['name']}** ({candidate['votes']} votes)")

    # 登出按鈕
        st.markdown("---")
        if st.button("Log out", key="logout"):
            self.app.clear_user_id()  # 清除登入 ID
            self.app.set_page("login")
            st.rerun()

    def show_add_vote_form(self):
        """新增投票箱表單"""
        st.markdown("---")
        st.subheader("Add a New Topic")

        # 初始化投票名稱
        if 'new_vote_name' not in st.session_state:
            st.session_state.new_vote_name = ''

        # 投票名稱輸入框
        vote_name = st.text_input("Topic Name", key="new_vote_name")

        # 初始化選項列表
        if "vote_options" not in st.session_state:
            st.session_state.vote_options = [""]

        # 顯示所有選項輸入框
        st.write("Add options:")
        options_to_remove = []
        for i, option in enumerate(st.session_state.vote_options):
            cols = st.columns([9, 1])
            with cols[0]:
                st.session_state.vote_options[i] = st.text_input(f"Option {i + 1}", value=option, key=f"vote_option_{i}")
            with cols[1]:
                if len(st.session_state.vote_options) > 1:
                    if st.button("－", key=f"remove_option_{i}"):
                        options_to_remove.append(i)

        # 移除選定的選項
        if options_to_remove:
            for idx in sorted(options_to_remove, reverse=True):
                st.session_state.vote_options.pop(idx)
            st.rerun()

        # 按鈕：新增選項輸入框
        if st.button("Add Option"):
            st.session_state.vote_options.append("")
            st.rerun()

        # 提交按鈕
        if st.button("Submit"):
            if vote_name and any(opt.strip() for opt in st.session_state.vote_options):
                try:
                    # 將非空選項組成列表並調用 add_vote 函數
                    option_list = [opt.strip() for opt in st.session_state.vote_options if opt.strip()]
                    result = doVote.add_vote(self.app.user_id, vote_name, *option_list)
                    if "error" in result:
                        st.error(f"Failed to add topic: {result['error']}")
                    else:
                        st.success(f"Topic '{vote_name}' added successfully!")
                        # 重置表單
                        del st.session_state.vote_options  # 重置選項
                        del st.session_state.new_vote_name  # 重置投票名稱
                        st.session_state.show_add_vote_form = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please provide a topic name and at least one valid option.")

        # 取消按鈕
        if st.button("Cancel"):
            st.session_state.show_add_vote_form = False
            del st.session_state.vote_options  # 重置選項
            del st.session_state.new_vote_name  # 重置投票名稱
            st.rerun()




class VoteBoxPage(Page):
    """Vote Box Detail Page"""

    def show(self):
        st.title(f"{self.app.current_vote_name}")

        # Ensure the user is logged in
        if self.app.user_id:
            pass
        else:
            st.error("Not logged in. Please return to the login page.")
            self.app.set_page("login")
            st.rerun()

        # Ensure a vote box is selected
        if not self.app.current_vote_box:
            st.error("No voting topic, please return to the voting topic selection page.")
            self.app.set_page("vote")
            st.rerun()

        # Add Options Button
        if "show_add_option_form" not in st.session_state:
            st.session_state.show_add_option_form = False


        with st.container():
            col1, col2 = st.columns([1, 1])
            with col2:
                if st.button("Add Options", key="add_options"):
                    st.session_state.show_add_option_form = True

        if st.session_state.show_add_option_form:
            st.markdown("### Add New Option")
            option_name = st.text_input("Option Name", key="new_option_name")

            if st.button("Submit Option"):
                if option_name.strip():
                    try:
                        result = doVote.add_vote_option(self.app.user_id, self.app.current_vote_box, option_name.strip())
                        if "error" in result:
                            st.error("Permission denied.")
                        else:
                            st.success(f"Option '{option_name}' added successfully!")
                            st.session_state.show_add_option_form = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error while adding option: {e}")
                else:
                    st.error("Please provide a valid option name.")

            if st.button("Cancel"):
                st.session_state.show_add_option_form = False
                st.rerun()

        # Auto-refresh mechanism
        refresh_interval = 10  # Refresh interval in seconds
        st_autorefresh(interval=refresh_interval * 1000, key="autorefresh_vote_box")


        # Fetch vote box options
        try:
            options = doVote.get_vote_options(self.app.current_vote_box)
        except Exception as e:
            st.error(f"Cannot get vote options: {e}")
            return

        # Placeholder for success and error messages
        success_message = st.empty()
        error_message = st.empty()

        # Display options
        for option in options:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"{option['name']}", key=f"vote_{option['name']}"):
                    try:
                        # Call doVote.vote API to vote
                        vote_result = doVote.vote(self.app.user_id, self.app.current_vote_box, option['name'])
                        if 'error' in vote_result:
                            error_message.error("You have already voted.")
                            time.sleep(3)
                            error_message.empty()
                        else:
                            success_message.success(f"Successfully voted for {option['name']}!")
                            time.sleep(3)
                            success_message.empty()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Voting failed: {e}")
            with col2:
                st.write(f"{option['votes']} votes")

        st.markdown("---")

        # Back to vote topic list
        if st.button("Back to Voting Topics"):
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
        if "current_vote_name" not in st.session_state:
            st.session_state.current_vote_name = None
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

    @property
    def current_vote_name(self):
        return st.session_state.current_vote_name

    @current_vote_name.setter
    def current_vote_name(self, vote_name):
        st.session_state.current_vote_name = vote_name

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
            st.error("Unknown page, navigating back to sign in page.")
            self.set_page("login")
            st.rerun()


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
