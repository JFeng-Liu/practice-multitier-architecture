# tier2_logic_3data/models.py
from tortoise.models import Model
from tortoise import fields

class Book(Model):
    """
    Model representing the internal book prices.
    Stores both USD and JPY prices to support multi-currency checkout.
    """
    id = fields.IntField(pk=True)  # Primary Key
    title = fields.CharField(max_length=100)
    price_usd = fields.DecimalField(max_digits=10, decimal_places=2) 
    price_jpy = fields.IntField()

    class Meta:
        table = "books"

    def __str__(self):
        return f"[{self.id}] {self.title}"

class TaxRate(Model):
    """
    Model representing regional tax rates.
    Unifies US states and JP into a single lookup table.
    """
    # Using region_code (e.g., 'NY', 'CA', 'JP') as the primary key
    region_code = fields.CharField(pk=True, max_length=5)
    # Tax rate stored as a high-precision decimal (e.g., 0.0950 for 9.5%)
    tax_rate = fields.DecimalField(max_digits=5, decimal_places=4)

    class Meta:
        table = "tax_rates"

    def __str__(self):
        return f"{self.region_code}: {self.tax_rate}"