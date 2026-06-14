"""Duplicate detection and removal for dashboard metrics."""

from .duplicate_detector import DuplicateDetector, MetricSignature

__all__ = ['DuplicateDetector', 'MetricSignature']
