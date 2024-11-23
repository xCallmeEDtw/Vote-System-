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
def create_vote(name: str, options: list[str]):
    try:
        # 自動生成名稱+時間戳作為唯一名稱
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_name = f"{name}_{timestamp}"

        vote_data = {
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
    try:
        # 取得投票的資料參考
        vote_ref = db.child("votes").child(vote_id)
        vote_data = vote_ref.get().val()

        # 確認投票是否存在
        if not vote_data:
            raise HTTPException(status_code=404, detail="Vote not found")

        # 確認選項是否已經存在
        if option in vote_data["options"]:
            raise HTTPException(status_code=400, detail="Option already exists")

        # 新增選項到 options
        vote_data["options"][option] = 0

        # 更新資料庫中的 options
        vote_ref.child("options").set(vote_data["options"])  # 使用 `set()` 確保直接覆蓋

        # 驗證資料庫是否成功更新
        updated_vote_data = vote_ref.get().val()
        if not updated_vote_data or option not in updated_vote_data["options"]:
            raise HTTPException(status_code=500, detail="Failed to add option in database")

        return {
            "message": "Option added successfully",
            "vote_id": vote_id,
            "updated_options": updated_vote_data["options"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add vote option: {str(e)}")

@app.post("/addUser")
def add_user(email: str, password: str):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user['idToken']
    except Exception as e:
        error = str(e)
        print(error)
        raise HTTPException(status_code=400, detail="User Exist")

@app.post("/login")
def add_user(email: str, password: str):
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