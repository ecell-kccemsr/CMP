from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))

    classrooms = relationship("Classroom", back_populates="teacher")

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    rtmp_key = Column(String, unique=True)
    status = Column(String, default="inactive")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_active = Column(DateTime(timezone=True))

    teacher = relationship("User", back_populates="classrooms")
    stream_metadata = relationship("StreamMetadata", back_populates="classroom")

class StreamMetadata(Base):
    __tablename__ = "stream_metadata"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    stream_start = Column(DateTime(timezone=True))
    stream_end = Column(DateTime(timezone=True))
    stream_quality = Column(JSON)
    viewer_count = Column(Integer, default=0)
    stream_status = Column(String)
    hls_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    classroom = relationship("Classroom", back_populates="stream_metadata")
