# python -m pytest tests/ -v
import pytest
import pytest_asyncio
import json
from tortoise import Tortoise
from tier2_logic_2calculation.jp_calculator import calculate_jp_order

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


async def test_jp_order_success_normal_discount():
    payload = json.dumps({
        "items": [
            {"book_id": 1, "quantity": 1}, # 2000 * 1 = 2000 JPY
            {"book_id": 2, "quantity": 1}  # 3000 * 1 = 3000 JPY
        ],
        "discount_percent": 20 # 20% off
    })
    
    result_str = await calculate_jp_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "success"
    assert result["total_price_wot"] == "5000"
    assert result["discounted_total_price_wot"] == "4000" # 5000 * 0.8 = 4000 JPY
    assert result["tax_amount"] == "400" # 4000 * 0.1 = 400 JPY
    assert result["total_price_wt"] == "4400" # 4000 + 400 = 4400 JPY
    assert len(result["warnings"]) == 0 # Should have NO warnings


async def test_jp_order_high_discount_warning():
    payload = json.dumps({
        "items": [{"book_id": 3, "quantity": 2}], # 4000 * 2 = 8000 JPY
        "discount_percent": 60 # 60% off (Triggers W001)
    })
    
    result_str = await calculate_jp_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "success"
    assert result["discounted_total_price_wot"] == "3200" # 8000 * 0.4 = 3200 JPY
    assert len(result["warnings"]) == 1
    assert result["warnings"][0]["warning_code"] == "W001"


async def test_jp_order_missing_discount():
    payload = json.dumps({
        "items": [{"book_id": 1, "quantity": 1}] # No discount_percent
    })
    
    result_str = await calculate_jp_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E002"


async def test_jp_order_invalid_discount_range():
    payload = json.dumps({
        "items": [{"book_id": 1, "quantity": 1}],
        "discount_percent": 150 
    }) # Invalid discount_percent (greater than 100)
    
    result_str = await calculate_jp_order(payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E002"


async def test_jp_order_bad_json():
    bad_payload = '{"items": [{"book_id":' # Invalid JSON
    result_str = await calculate_jp_order(bad_payload)
    result = json.loads(result_str)
    
    assert result["status"] == "failed"
    assert result["errors"][0]["error_code"] == "E000"