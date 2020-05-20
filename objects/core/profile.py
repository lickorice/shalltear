from __future__ import annotations

from datetime import datetime
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime
from sqlalchemy.orm import relationship

from config import BASE_EXPERIENCE
from objects.base import Base

class Profile(Base):
    __tablename__ = 'core_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    to_next = Column(Integer, default=BASE_EXPERIENCE)
    
    materia = Column(Integer, default=0)
    enabled = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Prestige Levels
    farm_prestige = Column(Integer, default=0)

    def __repr__(self):
        return "<Profile user_id={0.user_id}, level={0.level}>".format(self)

    @staticmethod
    def get_all_profiles(session):
        return session.query(Profile).all()

    @staticmethod
    def get_top_profiles(session, number=20):
        return session.query(Profile).order_by(Profile.level.desc()).all()[:number]

    @staticmethod
    def get_profile(user, session, create_if_not_exists=True):
        user_id = user.id
        result = session.query(Profile).filter_by(user_id=user_id).first()
        if result is None and create_if_not_exists:
            return Profile.create_profile(user, session, not user.bot)
        return result

    @staticmethod
    def create_profile(user, session, enabled, commit_on_execution=True):
        user_id = user.id
        new_profile = Profile(
            user_id = user_id,
            enabled = enabled,
        )
        session.add(new_profile)
        if commit_on_execution:
            session.commit()
        return new_profile