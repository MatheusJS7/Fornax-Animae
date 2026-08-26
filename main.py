from datetime import date, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from database import SessionLocal
from models import User, Task, Group
from auth import create_access_token
from liturgical import get_current_liturgical_period
from achievements import check_achievements, get_user_achievements, get_titles
from groups import create_group, list_user_groups, join_group, leave_group, get_group_ranking, get_group_tasks, create_group_task, update_group_streak
from sqlalchemy import or_
import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    from auth import verify_token
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    db = SessionLocal()
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

def reset_daily_tasks(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    today = date.today().isoformat()
    if user.last_active_date == today:
        return False
    db.query(Task).filter(Task.user_id == user_id, Task.completed == True).update({"completed": False})
    db.commit()
    return True

class UserCreate(BaseModel):
    email: str
    password: str
    nome: str | None = None

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    category: str | None = None
    xp_value: int = 10
    liturgical_period: str = "all"

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    xp_value: int | None = None
    liturgical_period: str | None = None

@app.post("/users")
def create_user(user: UserCreate):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = User(email=user.email, hashed_password=hashed.decode("utf-8"), nome=user.nome)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"id": db_user.id, "email": db_user.email, "nome": db_user.nome}

@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/liturgical/period")
def liturgical_period():
    period = get_current_liturgical_period()
    return period

@app.get("/users/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    reset_daily_tasks(db, current_user.id)
    user = db.query(User).filter(User.id == current_user.id).first()
    titles = get_titles(user)
    data = {
        "id": user.id, "email": user.email, "nome": user.nome,
        "xp": user.xp, "level": user.level, "streak": user.streak,
        "longest_streak": user.longest_streak, "total_tasks_done": user.total_tasks_done,
        "quaresma_sao_miguel": user.quaresma_sao_miguel,
        "level_title": titles["level_title"], "streak_title": titles["streak_title"],
    }
    db.close()
    return data

@app.put("/users/me/quaresma_sao_miguel")
def toggle_quaresma_sao_miguel(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    user.quaresma_sao_miguel = not user.quaresma_sao_miguel
    db.commit()
    status = user.quaresma_sao_miguel
    db.close()
    return {"quaresma_sao_miguel": status}

@app.get("/ranking")
def get_ranking(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    users = db.query(User).order_by(User.xp.desc()).all()
    ranking = [{"position": i + 1, "id": u.id, "nome": u.nome, "xp": u.xp, "level": u.level, "streak": u.streak, "level_title": get_titles(u)["level_title"], "streak_title": get_titles(u)["streak_title"]} for i, u in enumerate(users)]
    my_position = next((i + 1 for i, u in enumerate(users) if u.id == current_user.id), None)
    db.close()
    return {"ranking": ranking, "my_position": my_position}

@app.get("/users/me/achievements")
def my_achievements(current_user: User = Depends(get_current_user)):
    return get_user_achievements(current_user.id)

@app.get("/users/me/tasks")
def list_my_tasks(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    reset_daily_tasks(db, current_user.id)
    user = db.query(User).filter(User.id == current_user.id).first()
    period = get_current_liturgical_period()["period"]
    conditions = [
        (Task.liturgical_period == "all"),
        (Task.liturgical_period == period),
    ]
    if user.quaresma_sao_miguel:
        conditions.append(Task.liturgical_period == "quaresma_sao_miguel")
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        or_(*conditions)
    ).all()
    result = [{"id": t.id, "title": t.title, "completed": t.completed, "xp_value": t.xp_value, "category": t.category, "liturgical_period": t.liturgical_period} for t in tasks]
    db.close()
    return result

@app.post("/users/me/tasks")
def create_my_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_task = Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    result = {"id": db_task.id, "title": db_task.title, "completed": db_task.completed, "xp_value": db_task.xp_value, "liturgical_period": db_task.liturgical_period}
    db.close()
    return result

@app.get("/users")
def list_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return [{"id": u.id, "email": u.email, "nome": u.nome} for u in users]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if not user:
        return {"error": "Usuário não encontrado"}
    return {"id": user.id, "email": user.email, "nome": user.nome}

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        db.close()
        return {"error": "Usuário não encontrado"}
    db_user.email = user.email
    db_user.nome = user.nome
    if user.password:
        db_user.hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db.commit()
    db.close()
    return {"id": db_user.id, "email": db_user.email, "nome": db_user.nome}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return {"error": "Usuário não encontrado"}
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "Usuário deletado"}

@app.post("/users/{user_id}/tasks")
def create_task(user_id: int, task: TaskCreate):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    result = {"id": db_task.id, "title": db_task.title, "completed": db_task.completed, "xp_value": db_task.xp_value, "liturgical_period": db_task.liturgical_period}
    db.close()
    return result

@app.get("/users/{user_id}/tasks")
def list_tasks(user_id: int):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    db.close()
    return [{"id": t.id, "title": t.title, "completed": t.completed, "xp_value": t.xp_value, "category": t.category, "liturgical_period": t.liturgical_period} for t in tasks]

@app.get("/tasks")
def list_all_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return [{"id": t.id, "title": t.title, "category": t.category, "xp_value": t.xp_value, "liturgical_period": t.liturgical_period} for t in tasks]

@app.post("/tasks")
def create_task_admin(task: TaskCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_task = Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    result = {"id": db_task.id, "title": db_task.title, "category": db_task.category, "xp_value": db_task.xp_value, "liturgical_period": db_task.liturgical_period}
    db.close()
    return result

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    db = SessionLocal()
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        db.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.category is not None:
        db_task.category = task.category
    if task.xp_value is not None:
        db_task.xp_value = task.xp_value
    if task.liturgical_period is not None:
        db_task.liturgical_period = task.liturgical_period
    db.commit()
    result = {"id": db_task.id, "title": db_task.title, "category": db_task.category, "xp_value": db_task.xp_value, "liturgical_period": db_task.liturgical_period}
    db.close()
    return result

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    task.completed = True
    xp = task.xp_value
    task_user_id = task.user_id
    user = db.query(User).filter(User.id == task_user_id).first()
    user.xp += xp

    user.total_tasks_done += 1

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    if user.last_active_date == today:
        pass
    elif user.last_active_date == yesterday:
        user.streak += 1
    else:
        user.streak = 1

    if user.streak > user.longest_streak:
        user.longest_streak = user.streak

    user.last_active_date = today

    if user.xp >= 1600:
        user.level = 30
    elif user.xp >= 1200:
        user.level = 25
    elif user.xp >= 800:
        user.level = 20
    elif user.xp >= 500:
        user.level = 15
    elif user.xp >= 300:
        user.level = 10
    elif user.xp >= 150:
        user.level = 5
    elif user.xp >= 50:
        user.level = 2

    xp_total = user.xp
    streak = user.streak
    level = user.level
    longest_streak = user.longest_streak
    total_tasks_done = user.total_tasks_done
    user_level = user.level
    user_streak = user.streak
    db.commit()
    db.close()

    new_achievements = check_achievements(task_user_id)

    from achievements import get_level_title, get_streak_title

    return {
        "message": "Tarefa concluída!",
        "xp_ganho": xp,
        "xp_total": xp_total,
        "streak": streak,
        "level": level,
        "longest_streak": longest_streak,
        "total_tasks_done": total_tasks_done,
        "level_title": get_level_title(user_level),
        "streak_title": get_streak_title(user_streak),
        "new_achievements": new_achievements,
    }

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db.delete(task)
    db.commit()
    db.close()
    return {"message": "Tarefa deletada"}

class GroupCreate(BaseModel):
    name: str

class GroupTaskCreate(BaseModel):
    title: str
    category: str | None = None
    xp_value: int = 10

@app.post("/groups")
def create_group_endpoint(group: GroupCreate, current_user: User = Depends(get_current_user)):
    return create_group(group.name, current_user.id)

@app.get("/groups")
def list_my_groups(current_user: User = Depends(get_current_user)):
    return list_user_groups(current_user.id)

@app.post("/groups/{group_id}/join")
def join_group_endpoint(group_id: int, current_user: User = Depends(get_current_user)):
    ok = join_group(group_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=400, detail="Não foi possível entrar no grupo (não existe, cheio ou já é membro)")
    return {"message": "Entrou no grupo"}

@app.delete("/groups/{group_id}/leave")
def leave_group_endpoint(group_id: int, current_user: User = Depends(get_current_user)):
    ok = leave_group(group_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Você não é membro deste grupo")
    return {"message": "Saiu do grupo"}

@app.get("/groups/{group_id}/ranking")
def group_ranking(group_id: int, current_user: User = Depends(get_current_user)):
    return get_group_ranking(group_id)

@app.get("/groups/{group_id}/tasks")
def group_tasks(group_id: int, current_user: User = Depends(get_current_user)):
    return get_group_tasks(group_id)

@app.post("/groups/{group_id}/tasks")
def create_group_task_endpoint(group_id: int, task: GroupTaskCreate, current_user: User = Depends(get_current_user)):
    return create_group_task(group_id, task.title, task.category, task.xp_value, current_user.id)

@app.get("/groups/{group_id}/streak")
def group_streak(group_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        db.close()
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    data = {"group_id": group.id, "name": group.name, "streak": group.streak, "last_active_date": group.last_active_date}
    db.close()
    return data
