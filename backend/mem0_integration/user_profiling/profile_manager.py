from sqlalchemy.orm import Session
from ...api.users import crud as user_crud

class ProfileManager:
    def __init__(self, db: Session):
        self.db = db

    def update_user_profile(self, user_id: int, new_data: dict):
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update user profile with new data
        for key, value in new_data.items():
            setattr(user, key, value)
        
        self.db.commit()
        return user

    def get_user_profile(self, user_id: int):
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        return user