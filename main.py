from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="CyberPuls API", version="1.0.0")

# Настройка CORS, чтобы Telegram Mini App мог свободно стучаться на сервер
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель данных для выдачи LP через админку
class AdminActionRequest(BaseModel):
    admin_id: int
    target_user_id: int
    amount: int

# Список постоянных администраторов (можно вынести в переменные окружения)
DEFAULT_ADMINS = [8976502503]

@app.get("/")
def read_root():
    return {"status": "online", "project": "CyberPuls Blitz Tracker"}

# Эндпоинт проверки прав администратора
@app.get("/api/check-admin/{user_id}")
def check_admin(user_id: int):
    is_admin = user_id in DEFAULT_ADMINS
    return {"user_id": user_id, "is_admin": is_admin}

# Эндпоинт для начисления LP (пример логики для админки)
@app.post("/api/admin/give-lp")
def give_lp(data: AdminActionRequest):
    if data.admin_id not in DEFAULT_ADMINS:
        raise HTTPException(status_code=403, detail="Access denied: Root access required")
    
    # Здесь в будущем будет запрос к базе Supabase для обновления баланса игрока
    return {"success": True, "message": f"Successfully updated LP for user {data.target_user_id}"}
