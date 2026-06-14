"""
Comprehensive metric validation utilities.

Provides validation for:
1. Unit conversion and normalization
2. Calculation validation (especially for reductions)
3. Scope detection (subset vs total)
4. Value sanity checks

Matches the logic from metric_validation_utils.py in the reference implementation.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger


class UnitValidator:
    """Validates and standardizes unit handling."""
    
    # Unit conversion factors (to tons)
    UNIT_CONVERSIONS = {
        'gigatons': 1_000_000_000,
        'gt': 1_000_000_000,
        'gtco2e': 1_000_000_000,
        'million tons': 1_000_000,
        'mt': 1_000_000,
        'mtco2e': 1_000_000,
        'thousand tons': 1_000,
        'kt': 1_000,
        'ktco2e': 1_000,
        'tons': 1,
        't': 1,
        'tco2e': 1,
    }
    
    @classmethod
    def parse_value_and_unit(cls, value_str: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Parse a value string into number and unit.
        
        Args:
            value_str: String like "3,732,075 tons" or "33.338 million tons"
            
        Returns:
            Tuple of (numeric_value, unit) or (None, None) if parsing fails
        """
        if not value_str or not isinstance(value_str, str):
            return None, None
        
        # Remove commas from numbers
        value_str = value_str.replace(',', '')
        
        # Pattern 1: "123.45 million tons"
        pattern1 = r'([\d.]+)\s+(million\s+tons|gigatons?|thousand\s+tons|MtCO2e|GtCO2e|ktCO2e|tCO2e|tons?|Mt|Gt|kt|t)\b'
        match1 = re.search(pattern1, value_str, re.IGNORECASE)
        
        if match1:
            try:
                number = float(match1.group(1))
                unit = match1.group(2).strip()
                return number, unit
            except ValueError:
                pass
        
        # Pattern 2: Just a number (assume tons if in emissions context)
        pattern2 = r'^([\d.]+)$'
        match2 = re.match(pattern2, value_str.strip())
        if match2:
            try:
                number = float(match2.group(1))
                return number, 'tons'
            except ValueError:
                pass
        
        return None, None
    
    @classmethod
    def normalize_to_tons(cls, value: float, unit: str) -> Optional[float]:
        """
        Convert value to tons for comparison.
        
        Args:
            value: Numeric value
            unit: Unit string
            
        Returns:
            Value in tons, or None if unit not recognized
        """
        unit_lower = unit.lower().strip()
        
        # Try exact match first
        if unit_lower in cls.UNIT_CONVERSIONS:
            return value * cls.UNIT_CONVERSIONS[unit_lower]
        
        # Try partial matches
        for known_unit, factor in cls.UNIT_CONVERSIONS.items():
            if known_unit in unit_lower or unit_lower in known_unit:
                return value * factor
        
        return None
    
    @classmethod
    def validate_unit_consistency(cls, value_str1: str, value_str2: str, tolerance_pct: float = 0.01) -> Dict[str, Any]:
        """
        Check if two value strings represent the same value.
        
        Args:
            value_str1: First value string
            value_str2: Second value string
            tolerance_pct: Tolerance percentage (default 1%)
            
        Returns:
            Dict with 'consistent' (bool), 'message' (str), 'normalized_values' (tuple)
        """
        val1, unit1 = cls.parse_value_and_unit(value_str1)
        val2, unit2 = cls.parse_value_and_unit(value_str2)
        
        if val1 is None or val2 is None:
            return {
                'consistent': False,
                'message': 'Could not parse values',
                'normalized_values': (None, None)
            }
        
        norm1 = cls.normalize_to_tons(val1, unit1)
        norm2 = cls.normalize_to_tons(val2, unit2)
        
        if norm1 is None or norm2 is None:
            return {
                'consistent': False,
                'message': f'Unknown units: {unit1} or {unit2}',
                'normalized_values': (norm1, norm2)
            }
        
        if norm1 == 0 and norm2 == 0:
            consistent = True
        elif norm1 == 0 or norm2 == 0:
            consistent = False
        else:
            diff_pct = abs(norm1 - norm2) / max(norm1, norm2)
            consistent = diff_pct <= tolerance_pct
        
        message = 'Values are consistent' if consistent else f'Values differ: {norm1:,.0f} tons vs {norm2:,.0f} tons'
        
        return {
            'consistent': consistent,
            'message': message,
            'normalized_values': (norm1, norm2)
        }


class CalculationValidator:
    """Validates calculations, especially for reduction metrics."""
    
    @staticmethod
    def validate_reduction(baseline: str, current: str, reduction: str, 
                          metric_name: str, tolerance_pct: float = 0.05) -> Dict[str, Any]:
        """
        Validate that reduction = baseline - current (within tolerance).
        
        Args:
            baseline: Baseline value string
            current: Current value string
            reduction: Reduction value string
            metric_name: Name of metric for error reporting
            tolerance_pct: Tolerance percentage (default 5%)
            
        Returns:
            Dict with validation results
        """
        base_val, base_unit = UnitValidator.parse_value_and_unit(baseline)
        curr_val, curr_unit = UnitValidator.parse_value_and_unit(current)
        redu_val, redu_unit = UnitValidator.parse_value_and_unit(reduction)
        
        if base_val is None or curr_val is None or redu_val is None:
            return {
                'valid': False,
                'message': f'{metric_name}: Could not parse values',
                'expected_reduction': None,
                'actual_reduction': None,
                'severity': 'critical'
            }
        
        base_tons = UnitValidator.normalize_to_tons(base_val, base_unit)
        curr_tons = UnitValidator.normalize_to_tons(curr_val, curr_unit)
        redu_tons = UnitValidator.normalize_to_tons(redu_val, redu_unit)
        
        if base_tons is None or curr_tons is None or redu_tons is None:
            return {
                'valid': False,
                'message': f'{metric_name}: Unknown units',
                'expected_reduction': None,
                'actual_reduction': None,
                'severity': 'critical'
            }
        
        expected_reduction = abs(base_tons - curr_tons)
        
        if expected_reduction == 0:
            valid = redu_tons == 0
        else:
            diff_pct = abs(redu_tons - expected_reduction) / expected_reduction
            valid = diff_pct <= tolerance_pct
        
        message = (
            f'{metric_name}: Reduction calculation correct' if valid
            else f'{metric_name}: Reduction error - Expected {expected_reduction:,.0f} tons, got {redu_tons:,.0f} tons'
        )
        
        return {
            'valid': valid,
            'message': message,
            'expected_reduction': expected_reduction,
            'actual_reduction': redu_tons,
            'severity': 'critical' if not valid else 'ok',
            'error_magnitude': abs(redu_tons - expected_reduction) / expected_reduction if expected_reduction > 0 else 0
        }
    
    @staticmethod
    def validate_total_equals_sum(total: str, components: List[str], 
                                   metric_name: str, tolerance_pct: float = 0.05) -> Dict[str, Any]:
        """
        Validate that total equals sum of components.
        
        Args:
            total: Total value string
            components: List of component value strings
            metric_name: Name of metric for error reporting
            tolerance_pct: Tolerance percentage (default 5%)
            
        Returns:
            Dict with validation results
        """
        total_val, total_unit = UnitValidator.parse_value_and_unit(total)
        if total_val is None:
            return {
                'valid': False,
                'message': f'{metric_name}: Could not parse total value',
                'severity': 'critical'
            }
        
        total_tons = UnitValidator.normalize_to_tons(total_val, total_unit)
        
        component_tons = []
        for comp in components:
            comp_val, comp_unit = UnitValidator.parse_value_and_unit(comp)
            if comp_val is not None:
                comp_tons_val = UnitValidator.normalize_to_tons(comp_val, comp_unit)
                if comp_tons_val is not None:
                    component_tons.append(comp_tons_val)
        
        if not component_tons:
            return {
                'valid': False,
                'message': f'{metric_name}: Could not parse component values',
                'severity': 'high'
            }
        
        expected_total = sum(component_tons)
        
        if expected_total == 0:
            valid = total_tons == 0
        else:
            diff_pct = abs(total_tons - expected_total) / expected_total
            valid = diff_pct <= tolerance_pct
        
        message = (
            f'{metric_name}: Total calculation correct' if valid
            else f'{metric_name}: Total mismatch - Expected {expected_total:,.0f} tons, got {total_tons:,.0f} tons'
        )
        
        return {
            'valid': valid,
            'message': message,
            'expected_total': expected_total,
            'actual_total': total_tons,
            'severity': 'critical' if not valid else 'ok'
        }


class ScopeDetector:
    """Detects and validates metric scope (subset vs total)."""
    
    SUBSET_KEYWORDS = [
        'self-built', 'owned', 'operated by', 'proprietary', 'internal',
        'direct operations', 'specific', 'particular', 'certain',
        'data center only', 'facilities only', 'offices only'
    ]
    
    TOTAL_KEYWORDS = [
        'total', 'overall', 'company-wide', 'organization-wide', 'global',
        'all', 'entire', 'full', 'aggregate', 'combined', 'consolidated'
    ]
    
    @classmethod
    def detect_scope(cls, text: str, metric_name: str) -> Dict[str, Any]:
        """
        Detect if a metric is subset or total scope.
        
        Args:
            text: Context text where metric was found
            metric_name: Name of the metric
            
        Returns:
            Dict with 'scope', 'confidence', 'keywords_found'
        """
        text_lower = text.lower()
        metric_lower = metric_name.lower()
        
        subset_matches = [kw for kw in cls.SUBSET_KEYWORDS if kw in text_lower or kw in metric_lower]
        total_matches = [kw for kw in cls.TOTAL_KEYWORDS if kw in text_lower or kw in metric_lower]
        
        if len(total_matches) > len(subset_matches):
            return {
                'scope': 'total',
                'confidence': min(1.0, len(total_matches) / 3),
                'keywords_found': total_matches
            }
        elif len(subset_matches) > len(total_matches):
            return {
                'scope': 'subset',
                'confidence': min(1.0, len(subset_matches) / 3),
                'keywords_found': subset_matches
            }
        else:
            return {
                'scope': 'unclear',
                'confidence': 0.0,
                'keywords_found': []
            }
    
    @classmethod
    def validate_scope_consistency(cls, metric_name: str, metric_value: str, context: str) -> Dict[str, Any]:
        """
        Check if metric name and context have consistent scope.
        
        Args:
            metric_name: Name of the metric
            metric_value: Value of the metric
            context: Text context where metric was found
            
        Returns:
            Dict with validation results
        """
        name_scope = cls.detect_scope('', metric_name)
        context_scope = cls.detect_scope(context, '')
        
        if name_scope['scope'] == 'total' and context_scope['scope'] == 'subset':
            return {
                'consistent': False,
                'message': 'Metric name suggests total scope, but context suggests subset',
                'name_scope': name_scope,
                'context_scope': context_scope,
                'severity': 'high',
                'recommendation': 'Consider renaming metric to indicate subset scope or verify value represents total'
            }
        
        if name_scope['scope'] == 'subset' and context_scope['scope'] == 'total':
            return {
                'consistent': False,
                'message': 'Metric name suggests subset scope, but context suggests total',
                'name_scope': name_scope,
                'context_scope': context_scope,
                'severity': 'high',
                'recommendation': 'Consider renaming metric to indicate total scope or verify value represents subset'
            }
        
        return {
            'consistent': True,
            'message': 'Scope is consistent',
            'name_scope': name_scope,
            'context_scope': context_scope,
            'severity': 'ok'
        }


class MetricValidator:
    """Main validator that combines all validation types."""
    
    def __init__(self):
        self.unit_validator = UnitValidator()
        self.calc_validator = CalculationValidator()
        self.scope_detector = ScopeDetector()
    
    def validate_metrics(self, metrics: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate all metrics for quality issues.
        
        Args:
            metrics: List of metric dictionaries
            
        Returns:
            Tuple of (validated_metrics, validation_issues)
        """
        issues = []
        validated = []
        
        logger.info(f"Validating {len(metrics)} metrics for quality issues...")
        
        # Group metrics for cross-validation
        emissions_metrics = {}
        
        for metric in metrics:
            metric_name = metric.get('metric_name', '').lower()
            value_with_unit = metric.get('original_value_with_unit', '') or \
                             f"{metric.get('value', '')} {metric.get('unit', '') or ''}".strip()
            context = metric.get('category', '')
            
            # Collect emissions metrics for calculation validation
            if 'emission' in metric_name or 'scope' in metric_name or 'carbon' in metric_name:
                emissions_metrics[metric_name] = {
                    'value': value_with_unit,
                    'metric': metric,
                    'context': context
                }
            
            # Validate scope consistency for percentage metrics
            if '%' in value_with_unit:
                scope_result = ScopeDetector.validate_scope_consistency(
                    metric_name, value_with_unit, context
                )
                if not scope_result['consistent']:
                    issues.append({
                        'metric_name': metric.get('metric_name', ''),
                        'issue_type': 'scope_inconsistency',
                        'severity': scope_result['severity'],
                        'message': scope_result['message'],
                        'recommendation': scope_result.get('recommendation', '')
                    })
                    metric['validation_warning'] = scope_result['message']
            
            # Check for unit scale errors
            metric_issues = self._check_scale_errors(metric)
            if metric_issues:
                issues.extend(metric_issues)
                metric['validation_warning'] = metric_issues[0]['message']
            
            validated.append(metric)
        
        # Validate reduction calculations
        reduction_issues = self._validate_reduction_calculations(emissions_metrics)
        issues.extend(reduction_issues)
        
        # Log summary
        if issues:
            critical = sum(1 for i in issues if i.get('severity') == 'critical')
            high = sum(1 for i in issues if i.get('severity') == 'high')
            logger.warning(f"Found {len(issues)} validation issues: {critical} critical, {high} high priority")
        else:
            logger.info("No validation issues found")
        
        return validated, issues
    
    def _check_scale_errors(self, metric: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for potential 1000x scale errors."""
        issues = []
        
        metric_name = metric.get('metric_name', '').lower()
        value_str = str(metric.get('value', ''))
        unit_str = str(metric.get('unit', '') or '')
        
        if 'mtco2e' in unit_str.lower() or 'million tons' in unit_str.lower():
            try:
                val = float(value_str.replace(',', ''))
                if val > 100000:
                    issues.append({
                        'metric_name': metric.get('metric_name', ''),
                        'issue_type': 'unit_scale_error',
                        'severity': 'critical',
                        'message': f'Potential 1000x scale error: {value_str} {unit_str} seems too large',
                        'recommendation': f'Verify unit - should this be {val/1_000_000:.3f} million tons?'
                    })
            except ValueError:
                pass
        
        return issues
    
    def _validate_reduction_calculations(self, emissions_metrics: Dict) -> List[Dict[str, Any]]:
        """Validate reduction calculations across related metrics."""
        issues = []
        
        for metric_name, data in emissions_metrics.items():
            if 'reduction' not in metric_name:
                continue
            
            # Look for year in metric name
            year_matches = re.findall(r'20\d{2}', metric_name)
            if not year_matches:
                continue
            
            year = year_matches[0]
            
            # Determine scope
            scope_indicator = ''
            if 'scope_1' in metric_name or 'scope 1' in metric_name:
                scope_indicator = 'scope_1'
            elif 'scope_2' in metric_name or 'scope 2' in metric_name:
                scope_indicator = 'scope_2'
            elif 'scope_3' in metric_name or 'scope 3' in metric_name:
                scope_indicator = 'scope_3'
            
            if not scope_indicator:
                continue
            
            # Find baseline and current emissions
            prev_year = str(int(year) - 1)
            baseline_keys = [
                k for k in emissions_metrics.keys()
                if scope_indicator in k and prev_year in k and 'reduction' not in k
            ]
            current_keys = [
                k for k in emissions_metrics.keys()
                if scope_indicator in k and year in k and 'reduction' not in k
            ]
            
            if baseline_keys and current_keys:
                baseline_value = emissions_metrics[baseline_keys[0]]['value']
                current_value = emissions_metrics[current_keys[0]]['value']
                reduction_value = data['value']
                
                result = CalculationValidator.validate_reduction(
                    baseline_value,
                    current_value,
                    reduction_value,
                    metric_name
                )
                
                if not result['valid']:
                    issues.append({
                        'metric_name': metric_name,
                        'issue_type': 'calculation_error',
                        'severity': result['severity'],
                        'message': result['message'],
                        'error_magnitude': f"{result.get('error_magnitude', 0)*100:.1f}%"
                    })
        
        return issues
    
    def generate_validation_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of validation issues."""
        if not issues:
            return {
                'status': 'PASSED',
                'total_issues': 0,
                'critical_issues': 0,
                'high_priority_issues': 0,
                'message': 'All validations passed!'
            }
        
        critical = [i for i in issues if i.get('severity') == 'critical']
        high = [i for i in issues if i.get('severity') == 'high']
        
        return {
            'status': 'FAILED' if critical else 'WARNING',
            'total_issues': len(issues),
            'critical_issues': len(critical),
            'high_priority_issues': len(high),
            'issues': issues,
            'message': f'Found {len(issues)} validation issues ({len(critical)} critical, {len(high)} high priority)'
        }


def validate_metrics(metrics: List[Dict[str, Any]]) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Quick validation function for metrics list.
    
    Args:
        metrics: List of metric dictionaries
        
    Returns:
        Tuple of (validated_metrics, validation_summary)
    """
    validator = MetricValidator()
    validated, issues = validator.validate_metrics(metrics)
    summary = validator.generate_validation_summary(issues)
    return validated, summary
