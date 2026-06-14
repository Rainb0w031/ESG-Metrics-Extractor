"""
Duplicate detection and removal for dashboard metrics.

Matches the logic from integrate_esg_data_to_categorized_dashboard.py:
- create_metric_signature()
- detect_and_remove_all_duplicates()
"""

from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass
from loguru import logger


@dataclass
class MetricSignature:
    """
    Represents a unique signature for a metric.
    
    Used for duplicate detection across the dashboard.
    """
    metric_name: str
    value: str
    unit: str
    company: str
    year: str
    category: str
    type: str
    area: str
    
    def __hash__(self) -> int:
        """Make hashable for set operations."""
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        """Compare signatures."""
        if not isinstance(other, MetricSignature):
            return False
        return str(self) == str(other)
    
    def __str__(self) -> str:
        """String representation for duplicate detection."""
        fields = [
            self.metric_name,
            self.value,
            self.unit,
            self.company,
            self.year,
            self.category,
            self.type,
            self.area
        ]
        return "|".join(str(f).lower().strip() for f in fields)
    
    @classmethod
    def from_metric(cls, metric: Dict[str, Any]) -> 'MetricSignature':
        """Create signature from metric dictionary."""
        return cls(
            metric_name=metric.get('metric_name', ''),
            value=str(metric.get('value', '')),
            unit=str(metric.get('unit', '') or ''),
            company=metric.get('company', ''),
            year=str(metric.get('year', '')),
            category=metric.get('category', ''),
            type=metric.get('type', ''),
            area=metric.get('area', '')
        )


class DuplicateDetector:
    """
    Detects and removes duplicate metrics from dashboard data.
    
    Features:
    - Signature-based duplicate detection
    - Cross-company/year duplicate scanning
    - Tracking of removed duplicates
    - Configurable signature fields
    """
    
    def __init__(self, signature_fields: tuple = None):
        """
        Initialize detector.
        
        Args:
            signature_fields: Fields to use for signature creation
        """
        self.signature_fields = signature_fields or (
            'metric_name', 'value', 'unit', 'company', 
            'year', 'category', 'type', 'area'
        )
    
    def create_signature(self, metric: Dict[str, Any]) -> str:
        """
        Create a unique signature for a metric.
        
        Matches the reference implementation's create_metric_signature().
        
        Args:
            metric: Metric dictionary
            
        Returns:
            String signature for duplicate detection
        """
        key_fields = [
            str(metric.get(field, ''))
            for field in self.signature_fields
        ]
        
        return "|".join(key_fields).lower().strip()
    
    def detect_duplicates(self, 
                          metrics: List[Dict[str, Any]], 
                          source_label: str = "") -> Tuple[List[Dict], List[Dict]]:
        """
        Detect and separate duplicates from a list of metrics.
        
        Args:
            metrics: List of metric dictionaries
            source_label: Label for logging (e.g., "Amazon_2024")
            
        Returns:
            Tuple of (unique_metrics, duplicate_metrics)
        """
        seen_signatures: Set[str] = set()
        unique_metrics = []
        duplicates = []
        
        for metric in metrics:
            signature = self.create_signature(metric)
            
            if signature in seen_signatures:
                duplicates.append(metric)
                logger.debug(f"Duplicate found: {metric.get('metric_name', 'Unknown')} from {source_label}")
            else:
                unique_metrics.append(metric)
                seen_signatures.add(signature)
        
        if duplicates:
            logger.info(f"Found {len(duplicates)} duplicates in {source_label}")
        
        return unique_metrics, duplicates
    
    def clean_dashboard_duplicates(self, 
                                   dashboard_data: Dict[str, Any]) -> Tuple[Dict, List[Dict]]:
        """
        Detect and remove ALL duplicates from the entire dashboard.
        
        Matches the reference implementation's detect_and_remove_all_duplicates().
        
        Args:
            dashboard_data: Complete dashboard data dictionary
            
        Returns:
            Tuple of (cleaned_dashboard_data, removed_duplicates)
        """
        logger.info("Scanning entire dashboard for duplicates...")
        
        # Collect all metrics with source tracking
        all_metrics = []
        metric_sources = []
        
        for entry_key, entry_data in dashboard_data.items():
            company = entry_data.get("company", "")
            year = entry_data.get("year", "")
            metrics = entry_data.get("metrics", [])
            
            for metric in metrics:
                all_metrics.append(metric)
                metric_sources.append(f"{company}_{year}")
        
        logger.info(f"Total metrics in dashboard: {len(all_metrics)}")
        
        # Detect duplicates across all metrics
        seen_signatures: Set[str] = set()
        unique_indices = []
        removed_duplicates = []
        
        for i, metric in enumerate(all_metrics):
            signature = self.create_signature(metric)
            
            if signature in seen_signatures:
                removed_duplicates.append({
                    **metric,
                    '_source': metric_sources[i]
                })
                logger.debug(f"Removed duplicate: {metric.get('metric_name', 'Unknown')} from {metric_sources[i]}")
            else:
                unique_indices.append(i)
                seen_signatures.add(signature)
        
        # Reconstruct dashboard with unique metrics only
        cleaned_data = {}
        
        for entry_key, entry_data in dashboard_data.items():
            company = entry_data.get("company", "")
            year = entry_data.get("year", "")
            source_key = f"{company}_{year}"
            
            # Filter to only include unique metrics for this entry
            entry_unique_metrics = [
                all_metrics[i] 
                for i in unique_indices
                if metric_sources[i] == source_key
            ]
            
            cleaned_data[entry_key] = {
                **entry_data,
                'metrics': entry_unique_metrics
            }
        
        logger.info(f"Duplicates removed: {len(removed_duplicates)}")
        logger.info(f"Unique metrics remaining: {len(unique_indices)}")
        
        return cleaned_data, removed_duplicates
    
    def get_duplicate_summary(self, 
                              original_count: int, 
                              unique_count: int, 
                              duplicates: List[Dict]) -> Dict[str, Any]:
        """
        Generate a summary of duplicate cleaning.
        
        Args:
            original_count: Original metric count
            unique_count: Count after deduplication
            duplicates: List of removed duplicates
            
        Returns:
            Summary dictionary
        """
        return {
            'original_metrics_count': original_count,
            'unique_metrics_count': unique_count,
            'duplicates_removed': len(duplicates),
            'duplicate_rate': (original_count - unique_count) / original_count if original_count > 0 else 0,
            'cleaning_algorithm': 'signature_based_deduplication'
        }
