import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing imports...")

try:
    print("1. Testing src.models...")
    from src import models
    print("   ✓ models import successful")
    
    print("2. Testing src.database...") 
    from src import database
    print("   ✓ database import successful")
    
    print("3. Testing src.schema...")
    from src import schema
    print("   ✓ schema import successful")
    
    print("4. Testing src.auth...")
    from src import auth
    print("   ✓ auth import successful")
    
    print("5. Testing src.crud...")
    from src import crud
    print("   ✓ crud import successful")
    
    print("6. Testing src.main...")
    from src.main import app
    print("   ✓ main import successful")
    
    print("🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
