import asyncio
import traceback
import sys
from services.instagram import fetch_instagram

async def main():
    try:
        res = await fetch_instagram("https://www.instagram.com/p/DZOW9VgFvbl/")
        print("SUCCESS:")
        print(res)
    except Exception as e:
        print("ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
