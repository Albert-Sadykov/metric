"""Serializers for the metrics application."""

from rest_framework import serializers

from .models import Metric, MetricRecord, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class MetricSerializer(serializers.ModelSerializer):
    """Сериализатор метрик."""

    class Meta:
        model = Metric
        fields = ("id", "name", "description", "created_at")
        read_only_fields = ("id", "created_at")


class MetricRecordSerializer(serializers.ModelSerializer):
    """Сериализатор записей метрик."""

    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="tags",
    )

    class Meta:
        model = MetricRecord
        fields = ("id", "metric", "value", "timestamp", "tags", "tag_ids", "created_at")
        read_only_fields = ("id", "metric", "created_at")

