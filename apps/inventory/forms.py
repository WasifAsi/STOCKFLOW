from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import models

from .models import (
    Category,
    Product,
    ProductAttributeDefinition,
    StockLevel,
    StockMovement,
    StockTransfer,
    Supplier,
    Warehouse,
)


class CategorySelectForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select a category")


class ProductCreateForm(forms.Form):
    name = forms.CharField(max_length=200)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False, empty_label="No supplier")
    unit = forms.CharField(max_length=32, initial="pcs")
    reorder_point = forms.IntegerField(min_value=0, initial=0)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, category_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        chosen_category_id = category_id or self.data.get("category") or self.initial.get("category")
        if chosen_category_id:
            self.fields["category"].widget = forms.HiddenInput()
            self.fields["category"].initial = chosen_category_id

        if chosen_category_id:
            attribute_definitions = ProductAttributeDefinition.objects.filter(
                Q(category__isnull=True) | Q(category_id=chosen_category_id)
            ).order_by("sort_order", "name")
        else:
            attribute_definitions = ProductAttributeDefinition.objects.filter(category__isnull=True).order_by(
                "sort_order", "name"
            )

        self.attribute_definitions = list(attribute_definitions)

        for definition in self.attribute_definitions:
            field_name = f"attribute_{definition.id}"
            choices = [value.strip() for value in definition.allowed_values.split(",") if value.strip()]

            if choices:
                self.fields[field_name] = forms.ChoiceField(
                    label=definition.name,
                    choices=[("", "Select an option")] + [(choice, choice) for choice in choices],
                    required=definition.is_required,
                )
            elif definition.data_type == definition.DataType.INTEGER:
                self.fields[field_name] = forms.IntegerField(label=definition.name, required=definition.is_required)
            elif definition.data_type == definition.DataType.DECIMAL:
                self.fields[field_name] = forms.DecimalField(
                    label=definition.name,
                    required=definition.is_required,
                    max_digits=12,
                    decimal_places=2,
                )
            else:
                self.fields[field_name] = forms.CharField(label=definition.name, required=definition.is_required)

    def _attribute_values(self):
        values = {}
        for definition in self.attribute_definitions:
            value = self.cleaned_data.get(f"attribute_{definition.id}")
            if value in (None, ""):
                continue
            values[definition.name] = str(value).strip()
        return values

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("name") or not cleaned_data.get("category"):
            return cleaned_data

        attribute_values = self._attribute_values()
        generated_sku = Product.generate_sku(
            cleaned_data["name"],
            cleaned_data["category"],
            cleaned_data.get("supplier"),
            attribute_values,
        )
        cleaned_data["sku"] = generated_sku

        candidate_identity_parts = [
            cleaned_data["name"].strip().lower(),
            cleaned_data["category"].name.strip().lower(),
            cleaned_data.get("supplier").name.strip().lower() if cleaned_data.get("supplier") else "",
        ]
        candidate_identity_parts.extend(
            sorted(f"{key.strip().lower()}={value.strip().lower()}" for key, value in attribute_values.items() if value)
        )
        candidate_identity_key = "|".join(part for part in candidate_identity_parts if part)

        for product in Product.objects.select_related("category", "supplier").prefetch_related("attribute_values__definition"):
            if product.identity_key() == candidate_identity_key:
                self.add_error(
                    None,
                    "This product variant already exists. Name, size, colour, model, company, and category combination must be unique.",
                )
                break

        if Product.objects.filter(sku=generated_sku).exists():
            self.add_error(None, "A product with this generated SKU already exists.")

        return cleaned_data

    def save(self):
        product = Product.objects.create(
            sku=self.cleaned_data["sku"],
            name=self.cleaned_data["name"],
            category=self.cleaned_data["category"],
            supplier=self.cleaned_data.get("supplier"),
            unit=self.cleaned_data["unit"],
            reorder_point=self.cleaned_data["reorder_point"],
            is_active=self.cleaned_data.get("is_active", True),
        )

        for definition in self.attribute_definitions:
            value = self.cleaned_data.get(f"attribute_{definition.id}")
            if value in (None, ""):
                continue
            product.attribute_values.create(definition=definition, value=str(value))

        return product


class StockLevelForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.select_related("category"))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    quantity = forms.IntegerField(min_value=0, initial=0)
    reserved_quantity = forms.IntegerField(min_value=0, required=False, initial=0)

    def __init__(self, *args, product_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if product_queryset is not None:
            self.fields["product"].queryset = product_queryset

    def save(self):
        stock_level, _ = StockLevel.objects.update_or_create(
            product=self.cleaned_data["product"],
            warehouse=self.cleaned_data["warehouse"],
            defaults={
                "quantity": self.cleaned_data["quantity"],
                "reserved_quantity": self.cleaned_data.get("reserved_quantity", 0),
            },
        )
        return stock_level


class StockMovementForm(forms.Form):
    class MovementAction(models.TextChoices):
        NEW_STOCK = "RECEIPT", "New stock"
        SELL = "ISSUE", "Selling / issue"
        MOVE = "TRANSFER", "Move to another warehouse"

    action = forms.ChoiceField(choices=MovementAction.choices)
    product = forms.ModelChoiceField(queryset=Product.objects.select_related("category"))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all(), label="From warehouse")
    to_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="Select destination warehouse",
        label="To warehouse",
    )
    quantity = forms.IntegerField(min_value=1, initial=1)
    reference = forms.CharField(max_length=64, required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, product_queryset=None, warehouse_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        if product_queryset is not None:
            self.fields["product"].queryset = product_queryset

        if warehouse_queryset is not None:
            warehouses = list(warehouse_queryset)
            self.fields["warehouse"].queryset = warehouse_queryset
            self.fields["to_warehouse"].queryset = warehouse_queryset
        else:
            warehouses = list(Warehouse.objects.all())

        self.warehouses = warehouses

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        warehouse = cleaned_data.get("warehouse")
        to_warehouse = cleaned_data.get("to_warehouse")

        if action == self.MovementAction.MOVE and not to_warehouse:
            self.add_error("to_warehouse", "Select a destination warehouse for a transfer.")

        if action == self.MovementAction.MOVE and warehouse and to_warehouse and warehouse == to_warehouse:
            self.add_error("to_warehouse", "Destination warehouse must be different from the source warehouse.")

        return cleaned_data

    def save(self, performed_by):
        product = self.cleaned_data["product"]
        warehouse = self.cleaned_data["warehouse"]
        quantity = self.cleaned_data["quantity"]
        action = self.cleaned_data["action"]
        reference = self.cleaned_data.get("reference", "").strip()
        notes = self.cleaned_data.get("notes", "").strip()

        source_level, _ = StockLevel.objects.get_or_create(product=product, warehouse=warehouse)

        if action in {StockMovement.MovementType.RECEIPT, StockMovement.MovementType.ADJUSTMENT}:
            source_level.quantity += quantity
            source_level.save(update_fields=["quantity", "updated_at"])
            movement = StockMovement.objects.create(
                movement_type=StockMovement.MovementType.RECEIPT if action == StockMovement.MovementType.RECEIPT else StockMovement.MovementType.ADJUSTMENT,
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reference=reference,
                notes=notes,
                performed_by=performed_by,
            )
            return movement

        if action == StockMovement.MovementType.ISSUE:
            if source_level.quantity < quantity:
                raise ValidationError("Not enough stock available in this warehouse.")
            source_level.quantity -= quantity
            source_level.save(update_fields=["quantity", "updated_at"])
            movement = StockMovement.objects.create(
                movement_type=StockMovement.MovementType.ISSUE,
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reference=reference,
                notes=notes,
                performed_by=performed_by,
            )
            return movement

        if action == self.MovementAction.MOVE:
            to_warehouse = self.cleaned_data["to_warehouse"]
            if source_level.quantity < quantity:
                raise ValidationError("Not enough stock available in the source warehouse.")

            destination_level, _ = StockLevel.objects.get_or_create(product=product, warehouse=to_warehouse)
            source_level.quantity -= quantity
            destination_level.quantity += quantity
            source_level.save(update_fields=["quantity", "updated_at"])
            destination_level.save(update_fields=["quantity", "updated_at"])

            transfer = StockTransfer.objects.create(
                reference=reference or f"TRF-{product.sku}-{warehouse.code}-{to_warehouse.code}",
                product=product,
                quantity=quantity,
                from_warehouse=warehouse,
                to_warehouse=to_warehouse,
                requested_by=performed_by,
                approved_by=performed_by,
                status=StockTransfer.Status.RECEIVED,
                notes=notes,
            )
            StockMovement.objects.create(
                movement_type=StockMovement.MovementType.TRANSFER_OUT,
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reference=reference,
                notes=notes,
                transfer=transfer,
                performed_by=performed_by,
            )
            StockMovement.objects.create(
                movement_type=StockMovement.MovementType.TRANSFER_IN,
                product=product,
                warehouse=to_warehouse,
                quantity=quantity,
                reference=reference,
                notes=notes,
                transfer=transfer,
                performed_by=performed_by,
            )
            return transfer

        raise ValidationError("Unknown movement action.")
