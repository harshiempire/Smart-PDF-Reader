from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

class DBClient:
    __instance: AsyncIOMotorClient | None = None

    @staticmethod
    async def getInstance():
        if DBClient.__instance is None:
            try:
                # Use `asyncio.get_running_loop()` to ensure an active loop
                loop = asyncio.get_event_loop()
                DBClient.__instance = AsyncIOMotorClient(
                    "mongodb+srv://alleharshith:dnKUfZ1JnrmAoJt5@cluster0.5bitg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                    io_loop=loop
                )
                await DBClient.__instance.server_info()  # Ensure the database is connected
                return DBClient.__instance
            except RuntimeError as e:
                print(f"Failed to get running loop: {e}")
                return None
            except Exception as e:
                print(f"Database connection failed: {e}")
                return None
        return DBClient.__instance

    @staticmethod
    def disconnect():
        if DBClient.__instance is not None:
            DBClient.__instance.close()
            DBClient.__instance = None
