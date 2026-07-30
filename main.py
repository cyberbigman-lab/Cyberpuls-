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
    user_id: str  # ID пользователя, который пытается зайти в админку

@app.get("/")
def read_root():
    return {"status": "online", "project": "CyberPuls Blitz Tracker"}

@app.post("/api/admin/check")
def check_admin(data: AdminRequest):
    # Сравниваем прилетевший ID с тем, что записан на Render
    if not ADMIN_ID or str(data.user_id) != str(ADMIN_ID):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    return {"status": "ok", "message": "Добро пожаловать в админку!"}
    
