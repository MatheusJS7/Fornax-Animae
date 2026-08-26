from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_tasks_done = Column(Integer, default=0)
    last_active_date = Column(String(10), nullable=True)
    level = Column(Integer, default=1)
    quaresma_sao_miguel = Column(Boolean, default=False)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    xp_value = Column(Integer, default=10)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    liturgical_period = Column(String(20), default="all")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String(10), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    streak = Column(Integer, default=0)
    last_active_date = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

class GroupTask(Base):
    __tablename__ = "group_tasks"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    xp_value = Column(Integer, default=10)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
