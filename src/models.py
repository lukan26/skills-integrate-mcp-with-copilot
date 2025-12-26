"""
Database models for the High School Management System
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for many-to-many relationship between activities and participants
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('participant_id', Integer, ForeignKey('participants.id'), primary_key=True)
)


class Activity(Base):
    """Activity model representing an extracurricular activity"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)

    # Relationship to participants
    participants = relationship(
        "Participant",
        secondary=activity_participants,
        back_populates="activities"
    )

    def to_dict(self):
        """Convert activity to dictionary format"""
        return {
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants]
        }


class Participant(Base):
    """Participant model representing a student"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # Relationship to activities
    activities = relationship(
        "Activity",
        secondary=activity_participants,
        back_populates="participants"
    )
