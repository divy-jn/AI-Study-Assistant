import sys
import os

# Add the parent directory to sys.path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.core.config import settings

print(f"OLLAMA_MODEL={settings.OLLAMA_MODEL}")
