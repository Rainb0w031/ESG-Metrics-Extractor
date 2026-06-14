"""Data models for dashboard integration."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class IntegrationMetadata:
    """Metadata for integration tracking."""
    integration_date: str = ""
    total_metrics_processed: int = 0
    integration_algorithm: str = "enhanced_esg_metric_integration"
    duplicate_cleaning: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.integration_date:
            self.integration_date = datetime.now().isoformat()
        
        if not self.duplicate_cleaning:
            self.duplicate_cleaning = {
                'cleaning_date': datetime.now().isoformat(),
                'original_metrics_count': self.total_metrics_processed,
                'unique_metrics_count': self.total_metrics_processed,
                'duplicates_removed': 0,
                'cleaning_algorithm': 'individual_file_integration'
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'integration_date': self.integration_date,
            'total_metrics_processed': self.total_metrics_processed,
            'integration_algorithm': self.integration_algorithm,
            'duplicate_cleaning': self.duplicate_cleaning
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationMetadata':
        """Create from dictionary."""
        return cls(
            integration_date=data.get('integration_date', ''),
            total_metrics_processed=data.get('total_metrics_processed', 0),
            integration_algorithm=data.get('integration_algorithm', 'enhanced_esg_metric_integration'),
            duplicate_cleaning=data.get('duplicate_cleaning', {})
        )


@dataclass
class DashboardEntry:
    """Represents a single company/year entry in the categorized dashboard."""
    company: str
    year: str
    file_path: str = ""
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    integration_metadata: Optional[IntegrationMetadata] = None
    validation_summary: Optional[Dict[str, Any]] = None
    
    @property
    def key(self) -> str:
        """Get the unique key for this entry."""
        return f"{self.company}_{self.year}"
    
    @property
    def metrics_count(self) -> int:
        """Get the number of metrics."""
        return len(self.metrics)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'company': self.company,
            'year': self.year,
            'file_path': self.file_path,
            'metrics': self.metrics,
        }
        
        if self.integration_metadata:
            result['integration_metadata'] = self.integration_metadata.to_dict()
        
        if self.validation_summary:
            result['validation_summary'] = self.validation_summary
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DashboardEntry':
        """Create from dictionary."""
        metadata = None
        if 'integration_metadata' in data:
            metadata = IntegrationMetadata.from_dict(data['integration_metadata'])
        
        return cls(
            company=data.get('company', ''),
            year=data.get('year', ''),
            file_path=data.get('file_path', ''),
            metrics=data.get('metrics', []),
            integration_metadata=metadata,
            validation_summary=data.get('validation_summary')
        )


@dataclass 
class CategorizedDashboard:
    """Complete categorized dashboard containing multiple company/year entries."""
    entries: Dict[str, DashboardEntry] = field(default_factory=dict)
    
    def add_entry(self, entry: DashboardEntry, replace: bool = True) -> bool:
        """
        Add an entry to the dashboard.
        
        Args:
            entry: Dashboard entry to add
            replace: Whether to replace existing entry
            
        Returns:
            True if added/replaced, False if skipped
        """
        if entry.key in self.entries and not replace:
            return False
        
        self.entries[entry.key] = entry
        return True
    
    def get_entry(self, company: str, year: str) -> Optional[DashboardEntry]:
        """Get entry by company and year."""
        key = f"{company}_{year}"
        return self.entries.get(key)
    
    @property
    def total_entries(self) -> int:
        """Get total number of entries."""
        return len(self.entries)
    
    @property
    def total_metrics(self) -> int:
        """Get total metrics across all entries."""
        return sum(entry.metrics_count for entry in self.entries.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            key: entry.to_dict()
            for key, entry in self.entries.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategorizedDashboard':
        """Create from dictionary."""
        dashboard = cls()
        
        for key, entry_data in data.items():
            entry = DashboardEntry.from_dict(entry_data)
            dashboard.entries[key] = entry
        
        return dashboard
