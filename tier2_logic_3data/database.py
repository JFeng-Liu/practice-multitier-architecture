# tier2_logic_3data/database.py
from tortoise import Tortoise
import asyncio

# Import models from the new specific logic tier
from tier2_logic_3data.models import Book, TaxRate

async def init_db():
    print("Connecting to the database...")
    
    # 1. Initialize Tortoise ORM
    # Notice the path: We are placing the SQLite file strictly in tier3_data
    await Tortoise.init(
        db_url='sqlite://tier3_data/db.sqlite3',
        modules={'models': ['tier2_logic_3data.models']}
    )
    
    # 2. Generate schemas (Create tables)
    await Tortoise.generate_schemas()
    print("Database schemas generated successfully!")

    # 3. Seed Book Data
    book_count = await Book.all().count()
    if book_count == 0:
        print("Seeding initial book prices...")
        await Book.create(id=1, title="Red", price_usd="15.00", price_jpy=2000)
        await Book.create(id=2, title="Green", price_usd="20.00", price_jpy=3000)
        await Book.create(id=3, title="Blue", price_usd="25.00", price_jpy=4000)
    
    # 4. Seed Tax Rate Data
    tax_count = await TaxRate.all().count()
    if tax_count == 0:
        print("Seeding initial tax rates...")
        # Insert US State tax rates
        await TaxRate.create(region_code="NY", tax_rate="0.1000")
        await TaxRate.create(region_code="CA", tax_rate="0.0950")
        await TaxRate.create(region_code="TX", tax_rate="0.0800")
        # Insert Japan tax rate
        await TaxRate.create(region_code="JP", tax_rate="0.1000")

    print("Database initialization completed!")

if __name__ == "__main__":
    # Execute the async initialization function
    asyncio.run(init_db())