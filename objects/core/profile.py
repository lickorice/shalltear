from __future__ import annotations

from datetime import datetime
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime
from sqlalchemy.orm import relationship

from config import BASE_EXPERIENCE, EXP_FACTOR
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

    # Specialization Levels
    farm_prestige = Column(Integer, default=0)
    meme_stars = Column(Integer, default=0)

    def __repr__(self):
        return "<Profile user_id={0.user_id}, level={0.level}, exp={0.experience}, to_next={0.to_next}, materia={0.materia}>".format(self)

    @staticmethod
    def get_all_profiles(session):
        return session.query(Profile).all()

    @staticmethod
    def get_top_profiles(session, number=20):
        return session.query(Profile).order_by(Profile.level.desc()).all()[:number]

    @staticmethod
    def get_profile(user, session, create_if_not_exists=True, use_id=False):
        if use_id:
            user_id = user
        else:
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

    def level_up(self):
        self.level += 1
        self.experience = self.experience - self.to_next
        self.to_next = int(BASE_EXPERIENCE * (self.level ** EXP_FACTOR))

    def process_xp(self, exp_amount, session, commit_on_execution=True):
        self.experience += exp_amount
        leveled_up = False
        if self.experience >= self.to_next:
            self.level_up()
            leveled_up = True

        session.add(self)
        if commit_on_execution:
            session.commit()

        return leveled_up

    def apply_farm_prestige(self, session, raw_gil, commit_on_execution=True):
        new_materia = int(raw_gil / 1000000000000)
        self.materia += new_materia
        self.farm_prestige += 1
        session.add(self)
        if commit_on_execution:
            session.commit()
        return new_materia
