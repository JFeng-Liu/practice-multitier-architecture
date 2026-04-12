import json    # For handling JSON data
from tier2_logic_3data import repository    # For database access
from decimal import Decimal, ROUND_CEILING    # For precise rounding

async def calculate_jp_order(raw_json_string: str) -> str:
    """
    Expected raw_json_string format
    Calculate Japan order with multiple items.
    Rounds up to the nearest integer.
    """
    # ----- Parse JSON input -----
    try:
        data = json.loads(raw_json_string)
        items = data.get("items", [])
        discount_percent = data.get("discount_percent")
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
        
    # Check if discount is missing or out of valid range (E002)
    if discount_percent is None or int(discount_percent) < 0 or int(discount_percent) > 100:
        errors.append({
            "error_code": "E002",
        })
        
    # Error: If there are ANY errors, STOP execution and return immediately
    if len(errors) > 0:
        return json.dumps({
            "status": "failed",
            "errors": errors
        })

    # ----- If no errors -----
    total_price_wot = Decimal('0')

    # Loop through the items to calculate the total price without tax
    for item in items:
        book_id = item.get("book_id")
        # Get quantity
        quantity = Decimal(str(item.get("quantity", 0) or 0))
        # Get secure internal USD and JPY prices
        prices = await repository.get_book_data(book_id)
        # Get unit price in JPY
        unit_price = Decimal(str(prices["price_jpy"]))
        
        # Calculate total price without tax
        total_price_wot += unit_price * quantity
        
    # Apply discount
    discount_ratio = Decimal(str(discount_percent)) / Decimal('100')
    discounted_total_price_wot = (total_price_wot * (Decimal('1') - discount_ratio))\
        .quantize(Decimal('1'), rounding=ROUND_CEILING)
    
    # Calculate tax amount
    tax_rate = Decimal(str(await repository.get_region_tax_rate("JP")))
    tax_amount = (discounted_total_price_wot * tax_rate)\
        .quantize(Decimal('1'), rounding=ROUND_CEILING)
    
    # Calculate total price with tax
    total_price_wt = discounted_total_price_wot + tax_amount

    # warning handling
    warnings = []

    # Discount Warning
    if discount_percent >= 50:
        warnings.append({
            "warning_code": "W001"
        })
    
    return json.dumps({
        "status": "success",
        "region": "JP",
        "currency": "JPY",
        "total_price_wot": str(total_price_wot),
        "discounted_total_price_wot": str(discounted_total_price_wot),
        "tax_amount": str(tax_amount),
        "total_price_wt": str(total_price_wt),
        "errors": [],
        "warnings": warnings
    })
