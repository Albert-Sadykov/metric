"""URL routing for the metrics application."""

from django.urls import path

from . import views

app_name = "metrics"

urlpatterns = [
    # Tags
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    # Metrics
    path("metrics/", views.MetricListCreateView.as_view(), name="metric-list-create"),
    # Metric Records
    path(
        "metrics/<int:metric_id>/records/",
        views.MetricRecordListCreateView.as_view(),
        name="metric-record-list-create",
    ),
    path(
        "metrics/<int:metric_id>/records/<int:pk>/",
        views.MetricRecordDetailView.as_view(),
        name="metric-record-detail",
    ),
]

