import pytest
import asyncio
from db import DBClient

@pytest.mark.asyncio
async def test_singleton_instance():
    # Get instances using static method
    instance1 = await DBClient.getInstance()
    instance2 = await DBClient.getInstance()
    
    # Verify same instance
    assert instance1 is instance2

@pytest.mark.asyncio
async def test_connection():
    instance = await DBClient.getInstance()
    assert instance is not None

@pytest.mark.asyncio
async def test_disconnect():
    instance = await DBClient.getInstance()
    DBClient.disconnect()
    # Get new instance after disconnect
    new_instance = await DBClient.getInstance()
    assert new_instance is not None