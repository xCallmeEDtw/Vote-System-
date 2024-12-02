from fastapi import FastAPI, HTTPException, File, UploadFile

import pyrebase
from datetime import datetime


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

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
app = FastAPI()

@app.post("/createVote")
def create_vote(usertoken: str, name: str, options: list[str]):
    try:
        # 自動生成名稱+時間戳作為唯一名稱
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_name = f"{name}_{timestamp}"

        vote_data = {
            "user": usertoken,
            "name": unique_name,
            "created_at": datetime.now().isoformat(),
            "options": {option: 0 for option in options},
            "total_votes": 0,
            "voter_hashes": []
        }

        # 儲存投票（自動生成 ID）
        new_vote_ref = db.child("votes").push(vote_data)
        vote_id = new_vote_ref["name"]

        return {"message": "Vote created successfully", "vote_id": vote_id, "vote": vote_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create vote: {str(e)}")

@app.get("/Vote/{voteID}")
def view_vote(voteID: str):
    try:
        # 從 Firebase 資料庫中取得指定投票 ID 的詳細資訊
        vote_data = db.child("votes").child(voteID).get().val()
        
        if not vote_data:
            raise HTTPException(status_code=404, detail="Vote not found")

        return {"message": "Vote retrieved successfully", "vote_id": voteID, "vote": vote_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vote: {str(e)}")
<<<<<<< Updated upstream:backend/main.py

@app.get("/vote")
def all_vote():
    try:
        # 從 Firebase 資料庫中取得指定投票 ID 的詳細資訊
        vote_data = db.child("votes").get().val()
        
        if not vote_data:
            raise HTTPException(status_code=404, detail="Vote not found")

        return {"message": "", "vote": vote_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vote: {str(e)}")



@app.post("/addVoteOption")
def add_vote_option(vote_id: str, option: str):
=======
#-OCHXe0bM1M5NLCD0nCv
#eyJhbGciOiJSUzI1NiIsImtpZCI6IjkyODg2OGRjNDRlYTZhOThjODhiMzkzZDM2NDQ1MTM2NWViYjMwZDgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vb29wLTVmYjczIiwiYXVkIjoib29wLTVmYjczIiwiYXV0aF90aW1lIjoxNzMyMjU2NjIwLCJ1c2VyX2lkIjoiY3RLM1NCcmREUFVNUFdZWk5OSVdFSVk3WDVHMyIsInN1YiI6ImN0SzNTQnJkRFBVTVBXWVpOTklXRUlZN1g1RzMiLCJpYXQiOjE3MzIyNTY2MjAsImV4cCI6MTczMjI2MDIyMCwiZW1haWwiOiIxMjNhc2RAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbIjEyM2FzZEBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.EIam2-3rO4oLWTj94kigWD_cFEjjKUvaA4oaSb_a4KBaYDSMflYEdGqyDlXap9OW5JcKUh_pgIDCVCD4cCZFa5eCWgiQt0y4sasO3xPg7MaCqr8BA3yEmjKZQMfk1dBYkS8Odg6gKwpOSS4M-CstgCODHlgwvaJcCSlVkrCtVNlPhOhrnvKDtX3yrHut0xsXjfPvoO5u9mN3W3hd7_uZXxZ9pnRbNkObtZMC8JgdpT5DsEMGSyLE8CkC4QFJy0sZub-cI2xt_HrDEygXvjmN5y5cvNtJa-6sjT5SlD67SMDBPv-42CzdEAwd31akbA3Edb6PATAh4gWjzPSzD_uM4A
@app.post("/addVoteOption")
def add_vote_option(user_token: str, vote_id: str, option: str):
>>>>>>> Stashed changes:main.py
    try:
        # 從 Firebase 取得投票資料參考
        vote_ref = db.child("votes").child(vote_id)
        vote_data = vote_ref.get().val()

        # 確認投票是否存在
        if not vote_data:
            raise HTTPException(status_code=404, detail="Vote not found")

        # 確認使用者是否有權限
        if vote_data.get("user") != user_token:
            raise HTTPException(status_code=403, detail="User does not have permission to modify this vote")

        # 確認選項是否已經存在
        if option in db.child("votes").child(vote_id).get("options", {}):
            raise HTTPException(status_code=400, detail="Option already exists")
        # 在 Firebase votes 層更新 options 節點
        try:
            db.child("votes").child(vote_id).child("options").update({option: 0})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update options in Firebase: {str(e)}")

        # 確認是否成功更新

        return {
            "message": "Option added successfully",
            "vote_id": vote_id,
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

<<<<<<< Updated upstream:backend/main.py
=======
@app.post("/vote")
def vote(user_token: str, vote_id: str, option: str):
    try:
        # 從 Firebase 取得投票資料參考
        vote_ref = db.child("votes").child(vote_id)
        vote_data = vote_ref.get().val()

        # 確認投票是否存在
        if not vote_data:
            raise HTTPException(status_code=404, detail="Vote not found")

        # 確認選項是否有效
        if option not in vote_data.get("options", {}):
            raise HTTPException(status_code=400, detail="Invalid voting option")

        # 檢查用戶是否已經投票
        voter_hashes = vote_data.get("voter_hashes", [])
        if user_token in voter_hashes:
            raise HTTPException(status_code=403, detail="User has already voted")

        # 更新選項的票數
        current_votes = vote_data["options"].get(option, 0)
        new_votes = current_votes + 1

        # 新增用戶到 voter_hashes
        voter_hashes.append(user_token)
        print(current_votes)
        print(voter_hashes)
        # 更新 Firebase 資料庫
        try:
            db.child("votes").child(vote_id).update({
                f"options/{option}": new_votes,
                "voter_hashes": voter_hashes,
                "total_votes": vote_data.get("total_votes", 0) + 1
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update Firebase: {str(e)}")

        return {
            "message": "Vote successfully submitted",
            "vote_id": vote_id,
            "option": option,
            "new_votes": new_votes
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



>>>>>>> Stashed changes:main.py
@app.post("/addUser")
def add_user(email: str, password: str):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user['idToken']
    except Exception as e:
        error = str(e)
        print(error)
        if "6 characters" in error:
            raise HTTPException(status_code=400, detail="Password should be at least 6 characters")
        if "INVALID_EMAIL" in error:
            raise HTTPException(status_code=400, detail="Invaild Email")
        raise HTTPException(status_code=400, detail="User Exist")

@app.post("/login")
def login(email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user['idToken']
    except Exception as e:
        error = str(e)
        print(error)
        raise HTTPException(status_code=400, detail="User Not Exist or password Incorrect")


@app.post("/removeUser")
def removeUser(email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        auth.delete_user_account(user['idToken'])
    except:
        raise HTTPException(status_code=400, detail="User Not Exist or Incorrect password")