# tier2_logic_3data/repository.py
from tier2_logic_3data.models import Book, TaxRate
from decimal import Decimal
from typing import Optional

async def get_book_data(book_id: int) -> Optional[dict]:
    """
    Fetches raw book data from the database by ID.
    Returns a dictionary or None if not found.
    This abstracts the database source from the calculation layer.
    """
    book = await Book.get_or_none(id=book_id)
    if book:
        return {
            "id": book.id,
            "title": book.title,
            "price_usd": book.price_usd,
            "price_jpy": book.price_jpy
        }
    return None

async def get_region_tax_rate(region_code: str) -> Optional[Decimal]:
    """
    Fetches the tax rate for a specific region (e.g., 'NY', 'JP').
    Returns the tax rate as a Decimal or None.
    """
    tax_record = await TaxRate.get_or_none(region_code=region_code)
    if tax_record:
        return tax_record.tax_rate
    return None
