import traceback
try:
    from app.main import app
    print("App imported OK")
except Exception as e:
    traceback.print_exc()
