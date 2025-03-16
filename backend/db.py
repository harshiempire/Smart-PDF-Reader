from motor.motor_asyncio import AsyncIOMotorClient

class DBClient:
    _client: AsyncIOMotorClient | None = None

    @staticmethod
    async def connect() -> None:
        
        DBClient._client = AsyncIOMotorClient("mongodb+srv://alleharshith:dnKUfZ1JnrmAoJt5@cluster0.5bitg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        try:
            print(await DBClient._client.server_info())
        except Exception:
            print("Unable to connect")
    
    # @staticmethod
    def get_client():
        if DBClient._client is not None:
            return DBClient._client
        else:
            raise ConnectionError("Database not connected")