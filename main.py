import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

app = FastAPI()

# Читаем переменные окружения из Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

# Инициализация клиента Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class AdminRequest(BaseModel):
    user_id: str  # ID администратора

class GiveLpRequest(BaseModel):
    admin_id: str
    target_user_id: str
    amount: int

@app.get("/")
def read_root():
    return {"status": "online", "project": "CyberPuls Blitz Tracker"}

@app.post("/api/admin/check")
def check_admin(data: AdminRequest):
    if not ADMIN_ID or str(data.user_id) != str(ADMIN_ID):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return {"status": "ok", "message": "Добро пожаловать в админку!"}

@app.post("/api/admin/give-lp")
def give_lp(data: GiveLpRequest):
    # Проверка прав администратора на бэкенде
    if not ADMIN_ID or str(data.admin_id) != str(ADMIN_ID):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    if not supabase:
        raise HTTPException(status_code=500, detail="База данных не подключена")

    try:
        # Проверяем наличие пользователя в таблице 'users' (поля: telegram_id, lp)
        response = supabase.table("users").select("lp").eq("telegram_id", data.target_user_id).execute()
        
        if response.data and len(response.data) > 0:
            current_lp = response.data[0].get("lp", 0)
            new_lp = current_lp + data.amount
            supabase.table("users").update({"lp": new_lp}).eq("telegram_id", data.target_user_id).execute()
        else:
            supabase.table("users").insert({"telegram_id": data.target_user_id, "lp": data.amount}).execute()
            
        return {"status": "success", "message": f"Успешно изменено на {data.amount} LP"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
