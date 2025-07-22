#!/usr/bin/env python3
"""
Test script to verify the consolidated application imports correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    
    # Test core imports
    from core.database import get_async_db, init_db
    print("✅ Database imports successful")
    
    from core.config.settings import settings
    print("✅ Settings imports successful")
    
    # Test API imports
    from api.auth.routes import router as auth_router
    print("✅ Auth router imports successful")
    
    from api.users.routes import router as user_router
    print("✅ User router imports successful")
    
    # Test services imports
    from main.profile_memory import ProfileMemoryManager
    print("✅ Profile memory imports successful")
    
    from core.whiteboard import WhiteboardManager
    print("✅ Whiteboard imports successful")
    
    # Test main app
    from main import app
    print("✅ Main app imports successful")
    
    print("\n🎉 All imports successful! The consolidated application is ready.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 