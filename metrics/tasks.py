"""Celery tasks for the metrics application."""

import os
from datetime import datetime, timezone

from celery import shared_task
from django.conf import settings


@shared_task(name="metrics.tasks.generate_fake_report")
def generate_fake_report() -> str:
    """Generate a fake report with total counts of metrics and records.

    Creates / updates a text file in the REPORTS_DIR directory
    with the current count of Metric and MetricRecord objects.
    Runs every 2 minutes via Celery Beat.
    """
    from .models import Metric, MetricRecord  # local import to avoid AppRegistryNotReady

    reports_dir = getattr(settings, "REPORTS_DIR", settings.BASE_DIR / "reports")
    os.makedirs(reports_dir, exist_ok=True)

    total_metrics: int = Metric.objects.count()
    total_records: int = MetricRecord.objects.count()
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    content = (
        f"=== Fake Report ===\n"
        f"Generated at: {now}\n"
        f"Total metrics: {total_metrics}\n"
        f"Total records: {total_records}\n"
    )

    report_path = os.path.join(reports_dir, "fake_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Report generated: metrics={total_metrics}, records={total_records}"

