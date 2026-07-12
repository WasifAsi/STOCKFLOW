from decimal import Decimal

from django.db import migrations, models


def forwards(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")
    ProductAttributeDefinition = apps.get_model("inventory", "ProductAttributeDefinition")
    ProductAttributeValue = apps.get_model("inventory", "ProductAttributeValue")

    attribute_specs = [
        ("Brand", "TEXT", 1),
        ("Model", "TEXT", 2),
        ("Size", "TEXT", 3),
        ("Color", "TEXT", 4),
        ("Audience", "TEXT", 5),
        ("Price", "DECIMAL", 6),
    ]

    definitions = {}
    for name, data_type, sort_order in attribute_specs:
        definition, _ = ProductAttributeDefinition.objects.get_or_create(
            category=None,
            name=name,
            defaults={"data_type": data_type, "sort_order": sort_order},
        )
        definitions[name] = definition

    for product in Product.objects.all():
        legacy_values = {
            "Brand": getattr(product, "brand_name", ""),
            "Model": getattr(product, "model_name", ""),
            "Size": getattr(product, "size", ""),
            "Color": getattr(product, "color", ""),
            "Audience": getattr(product, "audience", ""),
            "Price": getattr(product, "price", None),
        }
        for label, raw_value in legacy_values.items():
            if raw_value in (None, "", Decimal("0")):
                continue
            ProductAttributeValue.objects.update_or_create(
                product=product,
                definition=definitions[label],
                defaults={"value": str(raw_value)},
            )


def backwards(apps, schema_editor):
    # Keep the data migration one-way; the old fixed columns are removed below.
    return


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_product_price"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductAttributeDefinition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("data_type", models.CharField(choices=[("TEXT", "Text"), ("DECIMAL", "Decimal"), ("INTEGER", "Integer")], default="TEXT", max_length=20)),
                ("allowed_values", models.TextField(blank=True, help_text="Optional comma-separated values for choices.")),
                ("is_required", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                        related_name="attribute_definitions",
                        to="inventory.category",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "name"],
                "unique_together": {("category", "name")},
            },
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.TextField(blank=True)),
                (
                    "definition",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="values",
                        to="inventory.productattributedefinition",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="attribute_values",
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "ordering": ["definition__sort_order", "definition__name"],
                "unique_together": {("product", "definition")},
            },
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="product", name="brand_name"),
        migrations.RemoveField(model_name="product", name="model_name"),
        migrations.RemoveField(model_name="product", name="size"),
        migrations.RemoveField(model_name="product", name="color"),
        migrations.RemoveField(model_name="product", name="audience"),
        migrations.RemoveField(model_name="product", name="price"),
    ]
