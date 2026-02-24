"""Views for the metrics application."""

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Metric, MetricRecord, Tag
from .serializers import MetricRecordSerializer, MetricSerializer, TagSerializer

RECORDS_CACHE_KEY_PREFIX = "metric_records_"
RECORDS_CACHE_TTL = 60 * 5  # 5 minutes


def _get_records_cache_key(metric_id: int) -> str:
    """Return cache key for metric records list."""
    return f"{RECORDS_CACHE_KEY_PREFIX}{metric_id}"


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------
@extend_schema_view(
    get=extend_schema(
        summary="Список тегов",
        description="Получить список всех доступных тегов.",
    ),
)
class TagListView(generics.ListAPIView):
    """GET /api/tags/ — список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
@extend_schema_view(
    get=extend_schema(
        summary="Список метрик",
        description="Получить список метрик текущего пользователя.",
    ),
    post=extend_schema(
        summary="Создание метрики",
        description="Создать новую метрику для текущего пользователя.",
    ),
)
class MetricListCreateView(generics.ListCreateAPIView):
    """GET /api/metrics/ — список метрик пользователя.
    POST /api/metrics/ — создание метрики.
    """

    serializer_class = MetricSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):  # type: ignore[override]
        return Metric.objects.filter(owner=self.request.user)

    def perform_create(self, serializer: MetricSerializer) -> None:
        serializer.save(owner=self.request.user)


# ---------------------------------------------------------------------------
# Metric Records
# ---------------------------------------------------------------------------
class MetricRecordMixin:
    """Mixin that resolves the parent metric and checks ownership."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_metric(self) -> Metric:
        """Return the parent metric; raise 404 if not found or not owned."""
        return get_object_or_404(
            Metric,
            pk=self.kwargs["metric_id"],  # type: ignore[attr-defined]
            owner=self.request.user,  # type: ignore[attr-defined]
        )


@extend_schema_view(
    get=extend_schema(
        summary="Список записей метрики",
        description="Получить список записей конкретной метрики (кэшируется).",
    ),
    post=extend_schema(
        summary="Создание записи метрики",
        description="Создать новую запись для конкретной метрики.",
    ),
)
class MetricRecordListCreateView(MetricRecordMixin, generics.ListCreateAPIView):
    """GET  /api/metrics/{metric_id}/records/ — кэшированный список записей.
    POST /api/metrics/{metric_id}/records/ — создание записи.
    """

    serializer_class = MetricRecordSerializer

    def get_queryset(self):  # type: ignore[override]
        metric = self.get_metric()
        return MetricRecord.objects.filter(metric=metric).select_related("metric").prefetch_related("tags")

    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Return cached list if available."""
        metric = self.get_metric()
        cache_key = _get_records_cache_key(metric.pk)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, RECORDS_CACHE_TTL)
        return response

    def perform_create(self, serializer: MetricRecordSerializer) -> None:
        metric = self.get_metric()
        serializer.save(metric=metric)
        # Invalidate cache after new record
        cache.delete(_get_records_cache_key(metric.pk))


@extend_schema_view(
    get=extend_schema(
        summary="Детализация записи метрики",
        description="Получить детализированную информацию об одной записи метрики.",
    ),
)
class MetricRecordDetailView(MetricRecordMixin, generics.RetrieveAPIView):
    """GET /api/metrics/{metric_id}/records/{pk}/ — детализация записи."""

    serializer_class = MetricRecordSerializer

    def get_queryset(self):  # type: ignore[override]
        metric = self.get_metric()
        return MetricRecord.objects.filter(metric=metric).select_related("metric").prefetch_related("tags")

