import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

ALLOWED_ADMINS = [8976502503, 8493889843]

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class AdminRequest(BaseModel):
    user_id: str

class GiveLpRequest(BaseModel):
    admin_id: str
    target_user_id: str
    amount: int

class UserGetRequest(BaseModel):
    user_id: str
    username: str = "Tanker"

@app.get("/")
def read_root():
    return {"status": "online", "project": "CyberPuls Blitz Tracker"}

@app.post("/api/admin/check")
def check_admin(data: AdminRequest):
    try:
        user_id_int = int(data.user_id)
    except ValueError:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if user_id_int not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    return {"status": "ok", "message": "Добро пожаловать в админку!"}

@app.post("/api/admin/give-lp")
def give_lp(data: GiveLpRequest):
    try:
        admin_id_int = int(data.admin_id)
    except ValueError:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if admin_id_int not in ALLOWED_ADMINS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    if not supabase:
        raise HTTPException(status_code=500, detail="База данных не подключена")

    try:
        response = supabase.table("users").select("lp").eq("telegram_id", data.target_user_id).execute()
        
        if response.data and len(response.data) > 0:
            current_lp = response.data[0].get("lp", 0)
            new_lp = current_lp + data.amount
            supabase.table("users").update({"lp": new_lp}).eq("telegram_id", data.target_user_id).execute()
        else:
            supabase.table("users").insert({"telegram_id": data.target_user_id, "lp": data.amount, "username": f"Игрок {str(data.target_user_id)[-4:]}"}).execute()
            
        return {"status": "success", "message": f"Успешно изменено на {data.amount} LP"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/get")
def get_user(data: UserGetRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="База данных не подключена")
    try:
        response = supabase.table("users").select("lp").eq("telegram_id", data.user_id).execute()
        if response.data and len(response.data) > 0:
            supabase.table("users").update({"username": data.username}).eq("telegram_id", data.user_id).execute()
            return {"status": "success", "lp": response.data[0].get("lp", 0)}
        else:
            supabase.table("users").insert({"telegram_id": data.user_id, "lp": 0, "username": data.username}).execute()
            return {"status": "success", "lp": 0}
    except Exception as e:
        try:
            response = supabase.table("users").select("lp").eq("telegram_id", data.user_id).execute()
            if response.data and len(response.data) > 0:
                return {"status": "success", "lp": response.data[0].get("lp", 0)}
            else:
                supabase.table("users").insert({"telegram_id": data.user_id, "lp": 0}).execute()
                return {"status": "success", "lp": 0}
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=str(inner_e))

@app.get("/api/leaders")
def get_leaders():
    if not supabase:
        raise HTTPException(status_code=500, detail="База данных не подключена")
    try:
        response = supabase.table("users").select("telegram_id, username, lp").order("lp", desc=True).limit(20).execute()
        return {"status": "success", "leaders": response.data if response.data else []}
    except Exception as e:
        try:
            response = supabase.table("users").select("telegram_id, lp").order("lp", desc=True).limit(20).execute()
            leaders = [{"telegram_id": u.get("telegram_id"), "username": f"Игрок {str(u.get('telegram_id'))[-4:]}", "lp": u.get("lp")} for u in response.data]
            return {"status": "success", "leaders": leaders}
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=str(inner_e))
            
