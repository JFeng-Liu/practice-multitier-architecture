# tests/test_gateway.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise
from tier2_logic_1gateway.main import app

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """
    Connect to DB before testing, close after testing.
    """
    await Tortoise.init(
        db_url='sqlite://tier3_data/db.sqlite3',
        modules={'models': ['tier2_logic_3data.models']}
    )
    yield
    await Tortoise.close_connections()


async def test_gateway_routing_to_jp():
    """
    Test if the gateway correctly routes the request to Japan calculator
    and returns the expected stringified JSON.
    """
    # Use ASGITransport to test the FastAPI app without running an actual server
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # Prepare the raw JSON payload
        payload = {
            "region": "JP",
            "items": [{"book_id": 1, "quantity": 1}],
            "discount_percent": 0
        }
        
        # Act: Send POST request
        response = await ac.post("/api/calculate", json=payload)
        
        # Assert: Check status and content
        assert response.status_code == 200
        data = response.json() # To Dictionary Type
        assert data["region"] == "JP"
        assert data["status"] == "success"
        assert isinstance(data["total_price_wt"], str) # Verify that numbers are strings


async def test_gateway_unknown_region():
    """
    Test the gateway's defensive logic when an unknown region is provided.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"region": "MARS", "items": []} # Invalid region
        
        response = await ac.post("/api/calculate", json=payload)
        
        assert response.status_code == 400
        assert "Unknown region" in response.json()["errors"][0]["message"]