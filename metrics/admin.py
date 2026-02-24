"""Admin panel configuration for the metrics application."""

from django.contrib import admin

from .models import Metric, MetricRecord, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""

    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


class MetricRecordInline(admin.TabularInline):
    """Inline display of records inside Metric admin page."""

    model = MetricRecord
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("value", "timestamp", "tags", "created_at")


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    """Admin configuration for Metric model."""

    list_display = ("id", "name", "owner", "created_at")
    list_filter = ("owner", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at",)
    inlines = (MetricRecordInline,)
    ordering = ("-created_at",)


@admin.register(MetricRecord)
class MetricRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MetricRecord model."""

    list_display = ("id", "metric", "value", "timestamp", "created_at")
    list_filter = ("metric", "tags", "timestamp")
    search_fields = ("metric__name",)
    readonly_fields = ("created_at",)
    filter_horizontal = ("tags",)
    ordering = ("-timestamp",)

