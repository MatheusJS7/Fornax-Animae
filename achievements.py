from datetime import date
from database import SessionLocal
from models import User, Achievement


ACHIEVEMENTS = [
    {"id": "a1",  "icon": "I",    "name": "Primeiro Passo",  "desc": "Complete a 1ª tarefa"},
    {"id": "a2",  "icon": "III",  "name": "3 dias seguidos", "desc": "Streak de 3 dias"},
    {"id": "a3",  "icon": "VII",  "name": "Semana fiel",     "desc": "7 dias de sequência"},
    {"id": "a4",  "icon": "L",    "name": "50 tarefas",      "desc": "Complete 50 tarefas"},
    {"id": "a5",  "icon": "XXX",  "name": "Mês fiel",        "desc": "30 dias de sequência"},
    {"id": "a6",  "icon": "X",    "name": "Soldado",         "desc": "Chegue ao marco 10"},
    {"id": "a7",  "icon": "XIII", "name": "Cavaleiro",       "desc": "Chegue ao marco 13"},
    {"id": "a8",  "icon": "XV",   "name": "Campeão",         "desc": "Chegue ao marco 15"},
    {"id": "a9",  "icon": "XX",   "name": "Guardião da Fé",  "desc": "Chegue ao marco 20"},
    {"id": "a10", "icon": "XXX",  "name": "Guardião da Alma", "desc": "Chegue ao marco 30"},
]


LEVEL_TITLES = [
    (1,  "Minério Bruto"),
    (5,  "Metal em Chamas"),
    (10, "Aço Temperado"),
    (13, "Monge"),
    (15, "Monge Forjado"),
    (18, "Lâmina Afiada"),
    (20, "Guardião da Fé"),
    (25, "Aço Inquebrável"),
    (30, "Guardião da Alma"),
    (40, "Mestre Ferreiro"),
    (50, "Obra-Prima"),
]

STREAK_TITLES = [
    (3,   "Fagulha"),
    (7,   "Brasa Viva"),
    (14,  "Fogo Constante"),
    (30,  "Monge"),
    (60,  "Monge do Fogo Perpétuo"),
    (100, "Forja Inextinguível"),
    (180, "Pilar de Brasa"),
    (365, "Um Ano na Forja"),
]


def get_level_title(level: int) -> str:
    title = "Minério Bruto"
    for req_level, t in LEVEL_TITLES:
        if level >= req_level:
            title = t
    return title


def get_streak_title(streak: int) -> str:
    title = None
    for req_streak, t in STREAK_TITLES:
        if streak >= req_streak:
            title = t
    return title


def get_titles(user) -> dict:
    return {
        "level_title": get_level_title(user.level),
        "streak_title": get_streak_title(user.streak),
    }


def check_achievements(user_id: int) -> list:
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return []

    existing = {a.achievement_id for a in db.query(Achievement).filter(Achievement.user_id == user_id).all()}

    new_achievements = []
    checks = [
        ("a1",  user.total_tasks_done >= 1),
        ("a2",  user.streak >= 3 or user.longest_streak >= 3),
        ("a3",  user.streak >= 7 or user.longest_streak >= 7),
        ("a4",  user.total_tasks_done >= 50),
        ("a5",  user.streak >= 30 or user.longest_streak >= 30),
        ("a6",  user.level >= 10),
        ("a7",  user.level >= 13),
        ("a8",  user.level >= 15),
        ("a9",  user.level >= 20),
        ("a10", user.level >= 30),
    ]

    for ach_id, condition in checks:
        if ach_id not in existing and condition:
            db.add(Achievement(user_id=user_id, achievement_id=ach_id))
            new_achievements.append(ach_id)

    db.commit()
    db.close()
    return new_achievements


def get_user_achievements(user_id: int) -> list:
    db = SessionLocal()
    unlocked = {a.achievement_id for a in db.query(Achievement).filter(Achievement.user_id == user_id).all()}
    db.close()
    result = []
    for ach in ACHIEVEMENTS:
        result.append({
            "id": ach["id"],
            "icon": ach["icon"],
            "name": ach["name"],
            "desc": ach["desc"],
            "unlocked": ach["id"] in unlocked,
        })
    return result
