from database import SessionLocal
from models import Notification


ACHIEVEMENT_NAMES = {
    "a1": "Primeiro Passo",
    "a2": "3 dias seguidos",
    "a3": "Semana fiel",
    "a4": "50 tarefas",
    "a5": "Mês fiel",
    "a6": "Soldado",
    "a7": "Cavaleiro",
    "a8": "Campeão",
    "a9": "Guardião da Fé",
    "a10": "Guardião da Alma",
}

STREAK_MILESTONES = {3: "Fagulha", 7: "Brasa Viva", 14: "Fogo Constante", 30: "Monge", 60: "Monge do Fogo Perpétuo", 100: "Forja Inextinguível", 180: "Pilar de Brasa", 365: "Um Ano na Forja"}


def create_notification(user_id: int, type: str, title: str, message: str = None):
    db = SessionLocal()
    notif = Notification(user_id=user_id, type=type, title=title, message=message)
    db.add(notif)
    db.commit()
    db.close()


def notify_achievements(user_id: int, new_achievements: list):
    for ach_id in new_achievements:
        name = ACHIEVEMENT_NAMES.get(ach_id, ach_id)
        create_notification(user_id, "achievement", f"Conquista desbloqueada: {name}", f"Você desbloqueou a conquista '{name}'!")


def notify_streak_milestone(user_id: int, streak: int):
    if streak in STREAK_MILESTONES:
        title = STREAK_MILESTONES[streak]
        create_notification(user_id, "streak", f"Sequência de {streak} dias!", f"Você ganhou o título '{title}'. Continue firme!")


def get_user_notifications(user_id: int) -> list:
    db = SessionLocal()
    notifs = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.read.asc(), Notification.created_at.desc()).all()
    result = [{"id": n.id, "type": n.type, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else None} for n in notifs]
    db.close()
    return result


def mark_read(user_id: int, notif_id: int) -> bool:
    db = SessionLocal()
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user_id).first()
    if not notif:
        db.close()
        return False
    notif.is_read = True
    db.commit()
    db.close()
    return True


def mark_all_read(user_id: int):
    db = SessionLocal()
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    db.close()
