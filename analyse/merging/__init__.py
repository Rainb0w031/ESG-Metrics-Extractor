"""Result merging strategies for ESG analysis."""

from .base_merger import BaseMerger
from .esg_merger import ESGMerger
from .category_merger import CategoryMerger
from .section_merger import SectionMerger
from .duplicate_detector import DuplicateDetector

__all__ = [
    "BaseMerger",
    "ESGMerger",
    "CategoryMerger",
    "SectionMerger",
    "DuplicateDetector",
]

