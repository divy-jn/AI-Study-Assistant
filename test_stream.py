
import asyncio
import httpx
import json

async def test_stream():
    url = "http://localhost:8000/api/chat/stream"
    # We need a token? The endpoint requires auth.
    # Let's login first.
    
    async with httpx.AsyncClient() as client:
        import uuid
        username = f"test_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        # Register first
        print(f"Registering ({username})...")
        reg_res = await client.post("http://localhost:8000/api/auth/register", json={
            "username": username,
            "password": password,
            "full_name": "Test User",
            "email": f"{username}@example.com"
        })
        
        if reg_res.status_code == 200:
            print("Registration success")
        else:
            print(f"Registration failed: {reg_res.text}")
            return

        # Login
        print("Logging in...")
        login_res = await client.post("http://localhost:8000/api/auth/login", data={
            "username": username,
            "password": password
        })
        
        if login_res.status_code == 200:
            token = login_res.json()["access_token"]
            print("Login success")
        else:
            print(f"Login failed: {login_res.text}")
            return



        # Test Stream with Context
        print("\nTesting Stream with Context...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Turn 1
        query = "What is the capital of France? Give a one mark answer."
        print(f"\nTurn 1: {query}")
        async with client.stream("POST", url, json={"query": query}, headers=headers, timeout=120.0) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("type") == "chunk":
                        print(data["content"], end="", flush=True)
        print("\n[DONE]")






if __name__ == "__main__":
    asyncio.run(test_stream())
