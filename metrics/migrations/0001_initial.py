"""Initial migration for metrics app."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Metric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("description", models.TextField(blank=True, default="", verbose_name="Описание")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to=settings.AUTH_USER_MODEL, verbose_name="Владелец")),
            ],
            options={
                "verbose_name": "Метрика",
                "verbose_name_plural": "Метрики",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="MetricRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.FloatField(verbose_name="Значение")),
                ("timestamp", models.DateTimeField(verbose_name="Временная отметка")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("metric", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="records", to="metrics.metric", verbose_name="Метрика")),
                ("tags", models.ManyToManyField(blank=True, related_name="records", to="metrics.tag", verbose_name="Теги")),
            ],
            options={
                "verbose_name": "Запись метрики",
                "verbose_name_plural": "Записи метрик",
                "ordering": ["-timestamp"],
            },
        ),
    ]

