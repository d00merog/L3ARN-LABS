from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MultimodalSessionBase(BaseModel):
    session_type: str
    content_data: Optional[Dict[str, Any]] = None
    processed_result: Optional[str] = None
    confidence_score: Optional[float] = None


class MultimodalSessionCreate(MultimodalSessionBase):
    pass


class MultimodalSession(MultimodalSessionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SpeechRecognitionBase(BaseModel):
    audio_file_path: Optional[str] = None
    transcribed_text: Optional[str] = None
    language_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None


class SpeechRecognitionCreate(SpeechRecognitionBase):
    pass


class SpeechRecognition(SpeechRecognitionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HandwritingAnalysisBase(BaseModel):
    image_file_path: Optional[str] = None
    recognized_text: Optional[str] = None
    handwriting_style: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None


class HandwritingAnalysisCreate(HandwritingAnalysisBase):
    pass


class HandwritingAnalysis(HandwritingAnalysisBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GestureRecognitionBase(BaseModel):
    gesture_type: Optional[str] = None
    gesture_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None


class GestureRecognitionCreate(GestureRecognitionBase):
    pass


class GestureRecognition(GestureRecognitionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VisualProblemSolvingBase(BaseModel):
    problem_type: str
    image_file_path: Optional[str] = None
    problem_description: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None


class VisualProblemSolvingCreate(VisualProblemSolvingBase):
    pass


class VisualProblemSolving(VisualProblemSolvingBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MultimodalProcessingRequest(BaseModel):
    """Request for multimodal processing"""
    session_type: str  # speech, handwriting, gesture, visual
    content_data: Optional[Dict[str, Any]] = None
    file_data: Optional[bytes] = None
    processing_options: Optional[Dict[str, Any]] = None


class MultimodalProcessingResponse(BaseModel):
    """Response from multimodal processing"""
    success: bool
    processed_result: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None 