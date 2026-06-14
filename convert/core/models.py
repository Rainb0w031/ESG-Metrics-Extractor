"""Data models for dashboard conversion."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Metric:
    """Represents a single ESG metric."""
    metric_name: str
    value: str
    unit: Optional[str] = None
    description: str = ""
    category: str = ""
    type: str = ""
    area: str = ""
    subcategory: str = ""
    importance: str = "Medium"
    importance_reasoning: str = ""
    details: List[str] = field(default_factory=list)
    original_value_with_unit: Optional[str] = None
    validation_warning: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'area': self.area,
            'subcategory': self.subcategory,
            'importance': self.importance,
            'importance_reasoning': self.importance_reasoning,
            'details': self.details,
        }
        
        if self.original_value_with_unit:
            result['original_value_with_unit'] = self.original_value_with_unit
        
        if self.validation_warning:
            result['validation_warning'] = self.validation_warning
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create from dictionary."""
        return cls(
            metric_name=data.get('metric_name', ''),
            value=data.get('value', ''),
            unit=data.get('unit'),
            description=data.get('description', ''),
            category=data.get('category', ''),
            type=data.get('type', ''),
            area=data.get('area', ''),
            subcategory=data.get('subcategory', ''),
            importance=data.get('importance', 'Medium'),
            importance_reasoning=data.get('importance_reasoning', ''),
            details=data.get('details', []),
            original_value_with_unit=data.get('original_value_with_unit'),
            validation_warning=data.get('validation_warning'),
        )


@dataclass
class ValidationIssue:
    """Represents a validation issue with a metric."""
    metric_name: str
    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    message: str
    recommendation: str = ""
    error_magnitude: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'metric_name': self.metric_name,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'message': self.message,
        }
        
        if self.recommendation:
            result['recommendation'] = self.recommendation
        
        if self.error_magnitude:
            result['error_magnitude'] = self.error_magnitude
        
        return result


@dataclass
class DashboardData:
    """Complete dashboard data structure."""
    company: str
    year: str
    file_path: str
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    validation_summary: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'company': self.company,
            'year': self.year,
            'file_path': self.file_path,
            'metrics': self.metrics,
        }
        
        if self.validation_summary:
            result['validation_summary'] = self.validation_summary
        
        return result
