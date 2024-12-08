import requests

# FastAPI 伺服器的基本 URL

BASE_URL = "http://127.0.0.1:8000"

def get_candidates():
    try:
        # Firebase 配置
        firebaseConfig = {
            'apiKey': "AIzaSyA48DRQ0XckWKNCKeS71FxQUmddexVoO6E",
            'authDomain': "oop-5fb73.firebaseapp.com",
            'projectId': "oop-5fb73",
            'storageBucket': "oop-5fb73.firebasestorage.app",
            'messagingSenderId': "181974573983",
            'appId': "1:181974573983:web:b181c40d0530f50a5253aa",
            'measurementId': "G-CF43GV0G1V",
            'databaseURL': "https://oop-5fb73-default-rtdb.asia-southeast1.firebasedatabase.app/"
        }

        # 初始化 Firebase
        import pyrebase
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        
        # 獲取所有投票 ID
        votes = db.child("votes").get()
        if votes.val():
            vote_ids = [vote.key() for vote in votes.each()]
            
            # 構建 candidates 結構
            candidates = []
            for vote_id in vote_ids:
                response = requests.get(f"{BASE_URL}/Vote/{vote_id}")
                if response.status_code == 200:
                    vote_data = response.json()
                    # print(vote_data)
                    vote_name = vote_data["vote"].get("name", "No Name").rsplit("_", 1)[0]
                    total_votes = vote_data["vote"].get("total_votes", 0)
                    candidates.append({"name": vote_name, "votes": total_votes, "vote_id": vote_id})
                else:
                    print(f"Failed to retrieve vote ID: {vote_id}, Status Code: {response.status_code}")

            # 根據票數排序並添加排名
            candidates = sorted(candidates, key=lambda x: x["votes"], reverse=True)
            for rank, candidate in enumerate(candidates, start=1):
                candidate["rank"] = rank
                
            # 返回構建的 candidates 清單
            return candidates
        else:
            print("沒有找到任何投票資料")
            return []
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []

# # 呼叫函數並輸出結果
# if __name__ == "__main__":
#     candidates_list = get_candidates()
#     print("候選人清單:")
#     print(candidates_list)



def get_vote_options(vote_id):
    """
    獲取指定投票箱的選項及票數
    :param vote_id: 投票箱的唯一 ID
    :return: 返回選項清單，格式如 [{"name": "選項1", "votes": 10, "rank": 1}, ...]
    """
    try:
        # 調用 view_vote API 獲取投票箱詳細資料
        response = requests.get(f"{BASE_URL}/Vote/{vote_id}")
        if response.status_code == 200:
            vote_data = response.json()
            if "vote" not in vote_data:
                raise ValueError("無法解析 API 返回的投票數據")

            # 獲取選項及票數
            options = vote_data["vote"].get("options", {})
            result = []
            for option_name, votes in options.items():
                result.append({"name": option_name, "votes": votes})

            # 根據票數排序並添加排名
            result = sorted(result, key=lambda x: x["votes"], reverse=True)
            for rank, option in enumerate(result, start=1):
                option["rank"] = rank

            return result
        else:
            print(f"無法獲取投票數據，狀態碼: {response.status_code}")
            return []
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []



def register_user(email: str, password: str):
    """
    使用 API 註冊用戶。
    :param email: 用戶的電子郵件地址
    :param password: 用戶的密碼
    :return: 成功返回 {'success': True}，失敗返回 {'error': ...}
    """
    url = f"{BASE_URL}/addUser"
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            return {"success": True}  # 註冊成功
        else:
            return {"error": response.json().get("detail", "未知錯誤")}
    except requests.exceptions.RequestException as e:
        return {"error": f"請求失敗: {str(e)}"}

# # 測試函數
# if __name__ == "__main__":
#     email = "testuser3@example.com"
#     password = "password123"
#     result = register_user(email, password)
#     print(result)

def login_user(email: str, password: str):
    """
    使用 API 登入用戶。
    :param email: 用戶的電子郵件地址
    :param password: 用戶的密碼
    :return: 成功返回 {'idToken': ...}，失敗返回 {'error': ...}
    """
    url = f"{BASE_URL}/login"
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            # 登入成功，返回 idToken
            return {"idToken":response.json()}
        else:
            # 返回錯誤信息
            return {"error": response.json().get("detail", "未知錯誤")}
    except requests.exceptions.RequestException as e:
        return {"error": f"請求失敗: {str(e)}"}

# # 測試函數
# if __name__ == "__main__":
#     email = "testuser3@example.com"
#     password = "password123"
#     result = login_user(email, password)
#     print(result)


def vote(user_token: str, vote_id: str, option: str):
    """
    使用 API 執行投票操作。
    :param user_token: 用戶的登入 token
    :param vote_id: 投票的 ID
    :param option: 用戶選擇的選項
    :return: 投票結果
    """
    url = f"{BASE_URL}/vote"
    payload = {
        "user_token": user_token,
        "vote_id": vote_id,
        "option": option
    }

    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            return response.json()  # 成功返回投票結果
        else:
            return {"error": response.json().get("detail", "未知錯誤")}
    except requests.exceptions.RequestException as e:
        return {"error": f"請求失敗: {str(e)}"}

# 測試程式碼
# if __name__ == "__main__":
#     # pass
#     # 測試登入
#     email = "1111@test.com"
#     password = "11111111"
#     login_result = login_user(email,password)

#     if "idToken" in login_result:
#         user_token = login_result["idToken"]
#         print("登入成功！")
        
#         # 測試投票
#         vote_id = "sample_vote_id"  # 替換為有效的投票 ID
#         option = "選項A"  # 替換為有效的選項
#         vote_result = vote(user_token, '-OC79nfuJ-p0HUM4Tq39', 'ㄚ木的店')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         # vote_result = vote(user_token, '-OC76ij8QVgi9l7VNKYS', 'string')
#         print("投票結果:", vote_result)
#     else:
#         print("登入失敗:", login_result.get("error", "未知錯誤"))

def add_vote(user_token, name, *options):
    """
    創建投票並新增選項
    :param user_token: 用戶的 ID Token
    :param name: 投票名稱
    :param options: 傳入的選項，作為可變參數
    :return: 返回創建的投票 ID 和選項結果
    """
    try:
        # 呼叫 createVote API，將參數傳遞到 query
        create_vote_response = requests.post(
            f"{BASE_URL}/createVote",
            params={"usertoken": user_token, "name": name},  # 將 token 和名稱放入查詢參數
            json=list(options)  # 選項作為列表傳入
        )

        if create_vote_response.status_code != 200:
            raise Exception(f"創建投票失敗: {create_vote_response.json().get('detail', '未知錯誤')}")

        # 解析投票 ID
        vote_id = create_vote_response.json()["vote_id"]
        print(f"投票已成功創建，ID: {vote_id}")

        # 返回結果
        return {"message": "投票和選項已成功創建", "vote_id": vote_id}

    except Exception as e:
        print(f"發生錯誤: {e}")
        return {"error": str(e)}

# if __name__ == "__main__":
#     """
#     測試 add_vote 函數
#     """
#     # 測試用戶登入
#     # email = "testuser3@example.com"
#     # password = "password123"


#     # user_token = login_user(email, password)['idToken']
#     # # print(user_token['idToken'])
#     # # # 測試數據
#     # vote_name = "今晚吃什麼3"
#     # options = ["火鍋", "燒烤", "拉麵", "壽司"]

#     # # 調用 add_vote 函數
#     # result = add_vote(user_token, vote_name, *options)

#     # # 打印結果
#     # print("測試結果:")
#     # if "error" in result:
#     #     print(f"測試失敗，錯誤信息: {result['error']}")
#     # else:
#     #     print(f"測試成功，投票 ID: {result['vote_id']}")
#     #     print(f"投票名稱: {vote_name}")
#     #     print(f"選項: {options}")
#     print(get_candidates()[0])



def add_vote_option(user_token, vote_id, option):
    """
    添加新的投票選項
    :param user_token: 用戶的 ID Token
    :param vote_id: 投票箱的 ID
    :param option: 新增的選項名稱
    :return: API 返回結果
    """
    try:
        # 調用 /addVoteOption API
        response = requests.post(
            f"{BASE_URL}/addVoteOption",
            params={"user_token": user_token, "vote_id": vote_id, "option": option}
        )

        if response.status_code != 200:
            raise Exception(f"新增選項失敗: {response.json().get('detail', '未知錯誤')}")

        # 返回成功結果
        return response.json()

    except Exception as e:
        print(f"發生錯誤: {e}")
        return {"error": str(e)}





# 執行測試
if __name__ == "__main__":
    def test_add_vote_option():
        """
        測試 add_vote_option 函數
        """
        # 測試用戶登入
        email = "testuser3@example.com"
        password = "password123"

        user_token = login_user(email, password)

        # 測試數據
        vote_id = "-OD1OQYGa1heuRySeW6K"  # 替換為真實的投票箱 ID
        option = "新的選項"

        # 調用 add_vote_option 函數
        result = add_vote_option(user_token, vote_id, option)

        # 打印結果
        print("測試結果:")
        if "error" in result:
            print(f"測試失敗，錯誤信息: {result['error']}")
        else:
            print(f"測試成功，新增選項: {option}")
            print(f"返回數據: {result}")    
    test_add_vote_option()
