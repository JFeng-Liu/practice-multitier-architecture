
import json    # For handling JSON data
from tier2_logic_3data import repository    # For database access
from decimal import Decimal, ROUND_CEILING    # For precise rounding

async def calculate_us_order(raw_json_string: str) -> str:
    """
    Expected raw_json_string format
    Calculate US order with multiple items.
    Rounds up to 2 decimal places.
    """
    # ----- Parse JSON input -----
    try:
        data = json.loads(raw_json_string)
        items = data.get("items", [])
        state_id = data.get("state_id")
    except json.JSONDecodeError:
        return json.dumps({
            "status": "failed",
            "errors": [{"error_code": "E000"}]  # E000: Invalid JSON format
        })

    # ----- Error handling -----
    errors = []
    
    # Check if no books are selected (E001)
    if not items or len(items) == 0:
        errors.append({
            "error_code": "E001",
        })
        
    # Check if state_id is missing (E003)
    if not state_id:
        errors.append({
            "error_code": "E003",
        })
        
    # Error: If there are ANY errors, STOP execution and return immediately
    if len(errors) > 0:
        return json.dumps({
            "status": "failed",
            "errors": errors
        })

    # ----- If no errors -----
    total_price_wot = Decimal('0.00')
    
    # Loop through the items to calculate the total price without tax
    for item in items:
        book_id = item.get("book_id")
        # Get quantity
        quantity = Decimal(str(item.get("quantity", 0) or 0))
        # Get secure internal USD and JPY prices
        prices = await repository.get_book_data(book_id)
        # Get unit price in USD
        unit_price = Decimal(str(prices["price_usd"])) 
        
        # Calculate total price without tax
        total_price_wot += unit_price * quantity
        
    # Get state tax rate and calculate tax amount
    tax_rate = Decimal(str(await repository.get_region_tax_rate(state_id)))
    tax_amount = (total_price_wot * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_CEILING)
    
    # Calculate total price with tax
    total_price_wt = total_price_wot + tax_amount
    
    return json.dumps({
        "status": "success",
        "region": "US",
        "currency": "USD",
        "total_price_wot": str(total_price_wot),
        "discounted_total_price_wot": str(total_price_wot),
        "tax_amount": str(tax_amount),
        "total_price_wt": str(total_price_wt),
        "errors": [],
        "warnings": []
    })
