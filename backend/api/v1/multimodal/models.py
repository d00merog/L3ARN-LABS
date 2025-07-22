from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main.database import Base


class MultimodalSession(Base):
    """Multimodal learning session data"""
    __tablename__ = "multimodal_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String, nullable=False)  # speech, handwriting, gesture, visual
    content_data = Column(JSON, nullable=True)  # Processed content data
    raw_data = Column(LargeBinary, nullable=True)  # Raw audio/image data
    processed_result = Column(Text, nullable=True)  # Processed result
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="multimodal_sessions")


class SpeechRecognition(Base):
    """Speech recognition and processing"""
    __tablename__ = "speech_recognition"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    audio_file_path = Column(String, nullable=True)
    transcribed_text = Column(Text, nullable=True)
    language_detected = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="speech_recognition_sessions")


class HandwritingAnalysis(Base):
    """Handwriting recognition and analysis"""
    __tablename__ = "handwriting_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_file_path = Column(String, nullable=True)
    recognized_text = Column(Text, nullable=True)
    handwriting_style = Column(String, nullable=True)  # cursive, print, mixed
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="handwriting_analysis_sessions")


class GestureRecognition(Base):
    """Gesture recognition and analysis"""
    __tablename__ = "gesture_recognition"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gesture_type = Column(String, nullable=True)  # wave, point, thumbs_up, etc.
    gesture_data = Column(JSON, nullable=True)  # Gesture coordinates and data
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="gesture_recognition_sessions")


class VisualProblemSolving(Base):
    """Visual problem solving and analysis"""
    __tablename__ = "visual_problem_solving"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_type = Column(String, nullable=False)  # math, science, geometry
    image_file_path = Column(String, nullable=True)
    problem_description = Column(Text, nullable=True)
    solution_steps = Column(JSON, nullable=True)  # Step-by-step solution
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="visual_problem_solving_sessions") 