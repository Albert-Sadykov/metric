"""Tests for the metrics application — MetricRecord creation endpoint."""

from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Metric, MetricRecord, Tag


class MetricRecordCreateTests(TestCase):
    """Test suite for POST /api/metrics/{metric_id}/records/."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass123",
        )
        self.metric = Metric.objects.create(
            name="Test Metric",
            description="A metric for testing",
            owner=self.user,
        )
        self.other_metric = Metric.objects.create(
            name="Other Metric",
            description="Belongs to another user",
            owner=self.other_user,
        )
        self.tag1 = Tag.objects.create(name="tag-alpha")
        self.tag2 = Tag.objects.create(name="tag-beta")
        self.url = reverse(
            "metrics:metric-record-list-create",
            kwargs={"metric_id": self.metric.pk},
        )
        self.valid_payload = {
            "value": 42.5,
            "timestamp": "2025-01-15T10:30:00Z",
        }

    # ------------------------------------------------------------------
    # Authentication tests
    # ------------------------------------------------------------------
    def test_create_record_unauthenticated(self) -> None:
        """Unauthenticated requests should be rejected with 401."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------
    # Success tests
    # ------------------------------------------------------------------
    def test_create_record_success(self) -> None:
        """Authenticated user can create a record for their metric."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MetricRecord.objects.count(), 1)
        record = MetricRecord.objects.first()
        assert record is not None
        self.assertEqual(record.value, 42.5)
        self.assertEqual(record.metric, self.metric)

    def test_create_record_with_tags(self) -> None:
        """Record can be created with associated tags."""
        self.client.force_authenticate(user=self.user)
        payload = {
            **self.valid_payload,
            "tag_ids": [self.tag1.pk, self.tag2.pk],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record = MetricRecord.objects.first()
        assert record is not None
        self.assertEqual(set(record.tags.values_list("pk", flat=True)), {self.tag1.pk, self.tag2.pk})

    def test_create_record_without_tags(self) -> None:
        """Record can be created without any tags."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record = MetricRecord.objects.first()
        assert record is not None
        self.assertEqual(record.tags.count(), 0)

    # ------------------------------------------------------------------
    # Validation tests
    # ------------------------------------------------------------------
    def test_create_record_missing_value(self) -> None:
        """Request without 'value' should return 400."""
        self.client.force_authenticate(user=self.user)
        payload = {"timestamp": "2025-01-15T10:30:00Z"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_record_missing_timestamp(self) -> None:
        """Request without 'timestamp' should return 400."""
        self.client.force_authenticate(user=self.user)
        payload = {"value": 42.5}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_record_invalid_value(self) -> None:
        """Non-numeric value should return 400."""
        self.client.force_authenticate(user=self.user)
        payload = {"value": "not-a-number", "timestamp": "2025-01-15T10:30:00Z"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Ownership / permission tests
    # ------------------------------------------------------------------
    def test_create_record_for_other_users_metric(self) -> None:
        """User should not be able to create records for metrics they don't own."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "metrics:metric-record-list-create",
            kwargs={"metric_id": self.other_metric.pk},
        )
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_record_nonexistent_metric(self) -> None:
        """Requesting a non-existent metric should return 404."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "metrics:metric-record-list-create",
            kwargs={"metric_id": 99999},
        )
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # Cache invalidation tests
    # ------------------------------------------------------------------
    def test_cache_invalidated_on_create(self) -> None:
        """After creating a record, the cached list should be invalidated."""
        from django.core.cache import cache as django_cache

        from .views import _get_records_cache_key

        self.client.force_authenticate(user=self.user)

        # Populate cache by listing records
        list_url = reverse(
            "metrics:metric-record-list-create",
            kwargs={"metric_id": self.metric.pk},
        )
        self.client.get(list_url)
        cache_key = _get_records_cache_key(self.metric.pk)
        self.assertIsNotNone(django_cache.get(cache_key))

        # Create record — cache should be invalidated
        self.client.post(list_url, self.valid_payload, format="json")
        self.assertIsNone(django_cache.get(cache_key))

    # ------------------------------------------------------------------
    # Response structure tests
    # ------------------------------------------------------------------
    def test_response_contains_expected_fields(self) -> None:
        """Response body should contain all expected fields."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        expected_fields = {"id", "metric", "value", "timestamp", "tags", "created_at"}
        self.assertTrue(expected_fields.issubset(set(data.keys())))

