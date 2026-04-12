# python -m pytest tests/ -v
import pytest
import pytest_asyncio
import json
from tortoise import Tortoise
from tier2_logic_2calculation.us_calculator import calculate_us_order

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


async def test_us_order_success():
    payload = json.dumps({
        "items": [
            {"book_id": 1, "quantity": 2}, # 15.00 * 2 = 30.00 USD
            {"book_id": 2, "quantity": 1}  # 20.00 * 1 = 20.00 USD
        ],
        "state_id": "NY" # 10% tax
    })
    result_str = await calculate_us_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "success"
    assert result["total_price_wot"] == "50.00" # 30.00 + 20.00 = 50.00 USD
    assert result["tax_amount"] == "5.00" # 50.00 * 0.1 = 5.00 USD
    assert result["total_price_wt"] == "55.00" # 50.00 + 5.00 = 55.00 USD
    assert len(result["warnings"]) == 0 # Should have NO warnings


async def test_us_order_empty_cart():
    payload = json.dumps({"items": [], "state_id": "NY"}) # No items in the cart
    result_str = await calculate_us_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E001"


async def test_us_order_empty_state():
    payload = json.dumps({"items": [], "state_id": ""}) # No items and no state ID
    result_str = await calculate_us_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E001"
    assert result["errors"][1]["error_code"] == "E003"


async def test_us_order_bad_json():
    bad_payload = '{"items": [{"book_id":' # Invalid JSON
    result_str = await calculate_us_order(bad_payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E000"