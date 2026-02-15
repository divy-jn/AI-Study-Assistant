import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import app modules
# Assuming we run this from backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
# If backend/ is the current dir, then we need to ensure backend/ matches the imports
sys.path.insert(0, current_dir)

from app.services.llm_service import OllamaLLMService
from app.core.config import settings

async def main():
    print(f"Checking configuration for model: {settings.OLLAMA_MODEL}")
    try:
        service = OllamaLLMService()
        available = await service.check_model_availability()
        if available:
            print("✅ Model is available and ready to use!")
    except Exception as e:
        print(f"❌ Model check failed: {e}")
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main())
