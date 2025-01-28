# Generated by Django 5.1.5 on 2025-01-28 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Embalse",
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
                ("fecha", models.DateField()),
                ("hora", models.TimeField()),
                ("nivel_embalse", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "db_table": "embalse",
                "unique_together": {("fecha", "hora")},
            },
        ),
    ]
