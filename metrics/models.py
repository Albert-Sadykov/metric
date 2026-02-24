"""Models for the metrics application."""

from django.conf import settings
from django.db import models


class Tag(models.Model):
    """Тег для записей метрик. Общий для всех пользователей."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Metric(models.Model):
    """Абстрактный показатель (трафик, продажи, температура и т.д.)."""

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Метрика"
        verbose_name_plural = "Метрики"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class MetricRecord(models.Model):
    """Запись значения метрики в определённый момент времени."""

    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Метрика",
    )
    value = models.FloatField(verbose_name="Значение")
    timestamp = models.DateTimeField(verbose_name="Временная отметка")
    tags = models.ManyToManyField(Tag, blank=True, related_name="records", verbose_name="Теги")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Запись метрики"
        verbose_name_plural = "Записи метрик"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.metric.name}: {self.value} @ {self.timestamp}"

