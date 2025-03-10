# Generated by Django 5.1.5 on 2025-01-28 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Instrumento",
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
                ("nombre", models.CharField(max_length=50)),
                ("fecha_alta", models.DateField(blank=True, null=True)),
                ("fecha_baja", models.DateField(blank=True, null=True)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "instrumento",
            },
        ),
        migrations.CreateModel(
            name="Tipo",
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
                ("nombre_tipo", models.CharField(max_length=50)),
                ("tipo_medicion", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "tipo",
            },
        ),
        migrations.CreateModel(
            name="Unidad",
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
                ("nombre_unidad", models.CharField(max_length=50)),
                ("simbolo", models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                "db_table": "unidad",
            },
        ),
        migrations.CreateModel(
            name="Parametro",
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
                ("nombre_parametro", models.CharField(max_length=50)),
                ("valor", models.DecimalField(decimal_places=4, max_digits=10)),
                (
                    "id_instrumento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="instrumento.instrumento",
                    ),
                ),
            ],
            options={
                "db_table": "parametro",
            },
        ),
        migrations.AddField(
            model_name="instrumento",
            name="id_tipo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="instrumento.tipo"
            ),
        ),
        migrations.AddField(
            model_name="tipo",
            name="id_unidad",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="instrumento.unidad"
            ),
        ),
    ]
