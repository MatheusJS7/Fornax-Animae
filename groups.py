from datetime import date
from database import SessionLocal
from models import Group, GroupMember, GroupTask, User


def create_group(name: str, owner_id: int) -> dict:
    db = SessionLocal()
    group = Group(name=name, owner_id=owner_id)
    db.add(group)
    db.commit()
    db.refresh(group)
    db.add(GroupMember(group_id=group.id, user_id=owner_id))
    db.commit()
    group_id = group.id
    db.close()
    return {"id": group_id, "name": name}


def list_user_groups(user_id: int) -> list:
    db = SessionLocal()
    memberships = db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    groups = []
    for m in memberships:
        g = db.query(Group).filter(Group.id == m.group_id).first()
        if g:
            member_count = db.query(GroupMember).filter(GroupMember.group_id == g.id).count()
            groups.append({"id": g.id, "name": g.name, "owner_id": g.owner_id, "streak": g.streak, "members": member_count})
    db.close()
    return groups


def join_group(group_id: int, user_id: int) -> bool:
    db = SessionLocal()
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        db.close()
        return False
    member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
    if member_count >= 10:
        db.close()
        return False
    existing = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).first()
    if existing:
        db.close()
        return False
    db.add(GroupMember(group_id=group_id, user_id=user_id))
    db.commit()
    db.close()
    return True


def leave_group(group_id: int, user_id: int) -> bool:
    db = SessionLocal()
    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).first()
    if not member:
        db.close()
        return False
    db.delete(member)
    db.commit()
    db.close()
    return True


def get_group_ranking(group_id: int) -> list:
    db = SessionLocal()
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    ranking = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            from achievements import get_level_title, get_streak_title
            ranking.append({"user_id": u.id, "nome": u.nome, "xp": u.xp, "level": u.level, "streak": u.streak, "level_title": get_level_title(u.level), "streak_title": get_streak_title(u.streak)})
    ranking.sort(key=lambda x: x["xp"], reverse=True)
    for i, r in enumerate(ranking):
        r["position"] = i + 1
    db.close()
    return ranking


def get_group_tasks(group_id: int) -> list:
    db = SessionLocal()
    tasks = db.query(GroupTask).filter(GroupTask.group_id == group_id).all()
    result = [{"id": t.id, "title": t.title, "category": t.category, "xp_value": t.xp_value, "created_by": t.created_by} for t in tasks]
    db.close()
    return result


def create_group_task(group_id: int, title: str, category: str, xp_value: int, user_id: int) -> dict:
    db = SessionLocal()
    task = GroupTask(group_id=group_id, title=title, category=category, xp_value=xp_value, created_by=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    result = {"id": task.id, "title": task.title, "category": task.category, "xp_value": task.xp_value}
    db.close()
    return result


def update_group_streak(group_id: int):
    db = SessionLocal()
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        db.close()
        return
    member_ids = [m.user_id for m in db.query(GroupMember).filter(GroupMember.group_id == group_id).all()]
    today = date.today().isoformat()
    yesterday = (date.today() - __import__('datetime').timedelta(days=1)).isoformat()
    all_active = True
    for uid in member_ids:
        user = db.query(User).filter(User.id == uid).first()
        if not user or user.last_active_date != today:
            all_active = False
            break
    if all_active and member_ids:
        if group.last_active_date == yesterday:
            group.streak += 1
        elif group.last_active_date != today:
            group.streak = 1
        group.last_active_date = today
    db.commit()
    db.close()
