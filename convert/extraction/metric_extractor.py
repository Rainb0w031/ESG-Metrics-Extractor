"""
Metric extraction from comprehensive ESG analysis.

Extracts all metrics from nested JSON structures using recursive search.
"""

from typing import Dict, List, Any
from loguru import logger


class MetricExtractor:
    """
    Extracts metrics from comprehensive ESG analysis.
    
    Features:
    - Recursive search through nested structures
    - Category determination from path
    - Subcategory detection
    - Details preservation
    """
    
    # Analysis sections to search
    ANALYSIS_SECTIONS = [
        "environmental_comprehensive_analysis",
        "social_comprehensive_analysis",
        "governance_comprehensive_analysis",
        "environmental_comprehensive",
        "social_comprehensive",
        "governance_comprehensive",
        # Simple format (from simplified prompt)
        "environmental",
        "social",
        "governance",
    ]
    
    def extract(self, analysis_data: Dict[str, Any], company: str, year: str) -> List[Dict[str, Any]]:
        """
        Extract all metrics from comprehensive analysis.
        
        Args:
            analysis_data: Comprehensive ESG analysis JSON
            company: Company name
            year: Report year
            
        Returns:
            List of metric dictionaries
        """
        metrics = []
        
        for section in self.ANALYSIS_SECTIONS:
            if section in analysis_data:
                logger.debug(f"Extracting from section: {section}")
                self._extract_recursive(
                    analysis_data[section],
                    path="",
                    parent_details=None,
                    metrics=metrics
                )
        
        logger.info(f"Extracted {len(metrics)} metrics from analysis")
        return metrics
    
    def _extract_recursive(self, 
                           data: Any,
                           path: str,
                           parent_details: List[str],
                           metrics: List[Dict[str, Any]]):
        """
        Recursively extract metrics from nested structures.
        
        Args:
            data: Current data node
            path: Current path in structure
            parent_details: Details from parent nodes
            metrics: List to append metrics to
        """
        if not isinstance(data, dict):
            return
        
        # Check if this level has details
        current_details = data.get("details", [])
        if current_details:
            parent_details = current_details
        
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if key == "metrics" and isinstance(value, dict):
                # Found a metrics section - extract all metrics
                for metric_name, metric_value in value.items():
                    if metric_value and metric_value != {} and metric_value != []:
                        metric = self._create_metric(
                            metric_name=metric_name,
                            metric_value=metric_value,
                            path=current_path,
                            parent_details=parent_details
                        )
                        metrics.append(metric)
            else:
                # Continue recursive search
                self._extract_recursive(value, current_path, parent_details, metrics)
    
    def _create_metric(self,
                       metric_name: str,
                       metric_value: Any,
                       path: str,
                       parent_details: List[str]) -> Dict[str, Any]:
        """
        Create a metric dictionary.
        
        Args:
            metric_name: Name of the metric
            metric_value: Value of the metric
            path: Path in the data structure
            parent_details: Details from parent nodes
            
        Returns:
            Metric dictionary
        """
        category = self._determine_category(path)
        subcategory = self._determine_subcategory(path)
        
        # Process details - replace underscores with spaces
        processed_details = []
        if parent_details:
            for detail in parent_details:
                if isinstance(detail, str):
                    processed_details.append(detail.replace("_", " "))
        
        return {
            "metric_name": metric_name,
            "value": metric_value,
            "unit": None,  # Will be extracted during cleaning
            "description": f"Metric from {path}",
            "category": category,
            "type": self._determine_type(category),
            "area": self._determine_area(category),
            "subcategory": subcategory,
            "importance": "Medium",  # Will be enhanced by LLM
            "details": processed_details
        }
    
    def _determine_category(self, path: str) -> str:
        """Determine ESG category from path."""
        path_lower = path.lower()
        
        environmental_keywords = [
            'environmental', 'emissions', 'energy', 'water', 
            'waste', 'carbon', 'climate', 'renewable'
        ]
        social_keywords = [
            'social', 'human', 'labor', 'community', 
            'employee', 'diversity', 'health', 'safety'
        ]
        governance_keywords = [
            'governance', 'board', 'ethics', 'compliance',
            'risk', 'transparency'
        ]
        
        if any(kw in path_lower for kw in environmental_keywords):
            return "E - environmental"
        elif any(kw in path_lower for kw in social_keywords):
            return "S - social"
        elif any(kw in path_lower for kw in governance_keywords):
            return "G - governance"
        else:
            return "E - environmental"  # Default
    
    def _determine_subcategory(self, path: str) -> str:
        """Determine subcategory from path."""
        path_lower = path.lower()
        
        subcategory_map = {
            ('emissions', 'scope', 'carbon'): 'Carbon Emissions',
            ('energy', 'renewable', 'electricity'): 'Energy',
            ('water',): 'Water',
            ('waste', 'packaging', 'recycling'): 'Waste',
            ('transportation', 'vehicle', 'logistics'): 'Transportation',
            ('building',): 'Buildings',
            ('supply_chain', 'supplier'): 'Supply Chain',
            ('employee', 'workforce', 'staff'): 'Employee',
            ('community', 'philanthrop'): 'Community',
            ('board', 'director'): 'Board',
            ('ethics', 'compliance'): 'Ethics',
            ('diversity', 'inclusion'): 'Diversity & Inclusion',
            ('safety', 'health'): 'Health & Safety',
        }
        
        for keywords, subcategory in subcategory_map.items():
            if any(kw in path_lower for kw in keywords):
                return subcategory
        
        return "Other"
    
    def _determine_type(self, category: str) -> str:
        """Determine metric type from category."""
        if category.startswith("E"):
            return "environmental"
        elif category.startswith("S"):
            return "social"
        elif category.startswith("G"):
            return "governance"
        return "environmental"
    
    def _determine_area(self, category: str) -> str:
        """Determine area from category."""
        if category.startswith("E"):
            return "E"
        elif category.startswith("S"):
            return "S"
        elif category.startswith("G"):
            return "G"
        return "E"
