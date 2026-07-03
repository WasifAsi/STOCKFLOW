from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=32, unique=True)
    location = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_warehouses",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    contact_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ProductAttributeDefinition(TimeStampedModel):
    class DataType(models.TextChoices):
        TEXT = "TEXT", "Text"
        DECIMAL = "DECIMAL", "Decimal"
        INTEGER = "INTEGER", "Integer"

    name = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="attribute_definitions",
        null=True,
        blank=True,
    )
    data_type = models.CharField(max_length=20, choices=DataType.choices, default=DataType.TEXT)
    allowed_values = models.TextField(blank=True, help_text="Optional comma-separated values for choices.")
    is_required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("category", "name")

    def __str__(self) -> str:
        if self.category:
            return f"{self.category.name}: {self.name}"
        return self.name


class ProductAttributeValue(TimeStampedModel):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="attribute_values")
    definition = models.ForeignKey(ProductAttributeDefinition, on_delete=models.CASCADE, related_name="values")
    value = models.TextField(blank=True)

    class Meta:
        unique_together = ("product", "definition")
        ordering = ["definition__sort_order", "definition__name"]

    def __str__(self) -> str:
        return f"{self.definition.name}: {self.value}"


class Product(TimeStampedModel):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    unit = models.CharField(max_length=32, default="pcs")
    reorder_point = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def attribute_summary(self) -> str:
        details = [f"{item.definition.name}: {item.value}" for item in self.attribute_values.select_related("definition")]
        return "; ".join(details)


class StockLevel(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_levels")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_levels")
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("product", "warehouse")
        ordering = ["product__name", "warehouse__name"]

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def __str__(self) -> str:
        return f"{self.product} @ {self.warehouse}"


class StockTransfer(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        IN_TRANSIT = "IN_TRANSIT", "In transit"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    reference = models.CharField(max_length=64, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transfers")
    quantity = models.PositiveIntegerField()
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="outgoing_transfers")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="incoming_transfers")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_transfers",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_transfers",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.reference


class StockMovement(TimeStampedModel):
    class MovementType(models.TextChoices):
        RECEIPT = "RECEIPT", "Receipt"
        ISSUE = "ISSUE", "Issue"
        TRANSFER_IN = "TRANSFER_IN", "Transfer in"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer out"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="movements")
    quantity = models.IntegerField()
    reference = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} - {self.product}"
