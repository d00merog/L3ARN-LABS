from sqlalchemy.orm import Session
from ...users import crud as user_crud
from fastapi import HTTPException
from typing import Dict, Any

class ProfileManager:
    def __init__(self, db: Session):
        self.db = db

    def update_user_profile(self, user_id: int, new_data: Dict[str, Any]) -> Dict[str, Any]:
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for key, value in new_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return user.dict()

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.dict()