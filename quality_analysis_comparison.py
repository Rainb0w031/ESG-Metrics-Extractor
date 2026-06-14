#!/usr/bin/env python3
"""
Quality Analysis Comparison Script

This script comprehensively analyzes our analysis results and compares them
with the reference Amazon 2022 comprehensive JSON to identify quality gaps
and areas for improvement.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict, Counter

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and return JSON file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return {}

def extract_metrics_from_section(section_data: Dict[str, Any], section_name: str = "") -> Dict[str, Any]:
    """Recursively extract all metrics from a section."""
    metrics = {}
    
    if isinstance(section_data, dict):
        for key, value in section_data.items():
            if key == "metrics" and isinstance(value, dict):
                # Found metrics object
                for metric_name, metric_value in value.items():
                    full_metric_name = f"{section_name}.{metric_name}" if section_name else metric_name
                    metrics[full_metric_name] = metric_value
            elif isinstance(value, dict):
                # Recursively search in nested objects
                nested_metrics = extract_metrics_from_section(value, f"{section_name}.{key}" if section_name else key)
                metrics.update(nested_metrics)
            elif isinstance(value, list):
                # Check if list contains dictionaries with metrics
                for item in value:
                    if isinstance(item, dict):
                        nested_metrics = extract_metrics_from_section(item, f"{section_name}.{key}" if section_name else key)
                        metrics.update(nested_metrics)
    
    return metrics

def extract_details_from_section(section_data: Dict[str, Any], section_name: str = "") -> List[str]:
    """Recursively extract all details from a section."""
    details = []
    
    if isinstance(section_data, dict):
        for key, value in section_data.items():
            if key == "details" and isinstance(value, list):
                # Found details list
                for detail in value:
                    if isinstance(detail, str):
                        details.append(detail)
            elif isinstance(value, dict):
                # Recursively search in nested objects
                nested_details = extract_details_from_section(value, f"{section_name}.{key}" if section_name else key)
                details.extend(nested_details)
            elif isinstance(value, list):
                # Check if list contains dictionaries with details
                for item in value:
                    if isinstance(item, dict):
                        nested_details = extract_details_from_section(item, f"{section_name}.{key}" if section_name else key)
                        details.extend(nested_details)
    
    return details

def analyze_metrics_quality(our_metrics: Dict[str, Any], reference_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the quality of metrics extraction."""
    analysis = {
        "total_our_metrics": len(our_metrics),
        "total_reference_metrics": len(reference_metrics),
        "unique_our_metrics": len(set(our_metrics.keys())),
        "unique_reference_metrics": len(set(reference_metrics.keys())),
        "metric_types_our": Counter(),
        "metric_types_reference": Counter(),
        "missing_metrics": [],
        "extra_metrics": [],
        "common_metrics": [],
        "quality_issues": []
    }
    
    # Analyze metric types (by naming patterns)
    for metric_name in our_metrics.keys():
        if "emissions" in metric_name.lower():
            analysis["metric_types_our"]["emissions"] += 1
        elif "energy" in metric_name.lower():
            analysis["metric_types_our"]["energy"] += 1
        elif "water" in metric_name.lower():
            analysis["metric_types_our"]["water"] += 1
        elif "waste" in metric_name.lower():
            analysis["metric_types_our"]["waste"] += 1
        elif "diversity" in metric_name.lower() or "inclusion" in metric_name.lower():
            analysis["metric_types_our"]["diversity_inclusion"] += 1
        elif "safety" in metric_name.lower() or "health" in metric_name.lower():
            analysis["metric_types_our"]["health_safety"] += 1
        elif "governance" in metric_name.lower() or "board" in metric_name.lower():
            analysis["metric_types_our"]["governance"] += 1
        else:
            analysis["metric_types_our"]["other"] += 1
    
    for metric_name in reference_metrics.keys():
        if "emissions" in metric_name.lower():
            analysis["metric_types_reference"]["emissions"] += 1
        elif "energy" in metric_name.lower():
            analysis["metric_types_reference"]["energy"] += 1
        elif "water" in metric_name.lower():
            analysis["metric_types_reference"]["water"] += 1
        elif "waste" in metric_name.lower():
            analysis["metric_types_reference"]["waste"] += 1
        elif "diversity" in metric_name.lower() or "inclusion" in metric_name.lower():
            analysis["metric_types_reference"]["diversity_inclusion"] += 1
        elif "safety" in metric_name.lower() or "health" in metric_name.lower():
            analysis["metric_types_reference"]["health_safety"] += 1
        elif "governance" in metric_name.lower() or "board" in metric_name.lower():
            analysis["metric_types_reference"]["governance"] += 1
        else:
            analysis["metric_types_reference"]["other"] += 1
    
    # Find missing and extra metrics
    our_metric_names = set(our_metrics.keys())
    reference_metric_names = set(reference_metrics.keys())
    
    analysis["missing_metrics"] = list(reference_metric_names - our_metric_names)
    analysis["extra_metrics"] = list(our_metric_names - reference_metric_names)
    analysis["common_metrics"] = list(our_metric_names & reference_metric_names)
    
    # Analyze quality issues
    for metric_name, metric_value in our_metrics.items():
        if not metric_value or metric_value == "":
            analysis["quality_issues"].append(f"Empty metric value: {metric_name}")
        elif isinstance(metric_value, str) and len(metric_value.strip()) < 3:
            analysis["quality_issues"].append(f"Very short metric value: {metric_name} = '{metric_value}'")
    
    return analysis

def analyze_details_quality(our_details: List[str], reference_details: List[str]) -> Dict[str, Any]:
    """Analyze the quality of details extraction."""
    analysis = {
        "total_our_details": len(our_details),
        "total_reference_details": len(reference_details),
        "unique_our_details": len(set(our_details)),
        "unique_reference_details": len(set(reference_details)),
        "avg_our_detail_length": sum(len(detail) for detail in our_details) / len(our_details) if our_details else 0,
        "avg_reference_detail_length": sum(len(detail) for detail in reference_details) / len(reference_details) if reference_details else 0,
        "short_details_our": [detail for detail in our_details if len(detail) < 50],
        "long_details_our": [detail for detail in our_details if len(detail) > 500],
        "quality_issues": []
    }
    
    # Analyze quality issues
    for detail in our_details:
        if len(detail) < 20:
            analysis["quality_issues"].append(f"Very short detail: '{detail[:50]}...'")
        elif len(detail) > 1000:
            analysis["quality_issues"].append(f"Very long detail: '{detail[:50]}...'")
        elif detail.strip() == "":
            analysis["quality_issues"].append("Empty detail")
    
    return analysis

def analyze_structure_quality(our_data: Dict[str, Any], reference_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the structural quality of the analysis."""
    analysis = {
        "our_sections": set(),
        "reference_sections": set(),
        "missing_sections": [],
        "extra_sections": [],
        "common_sections": [],
        "structure_issues": []
    }
    
    # Extract section names
    def extract_sections(data: Dict[str, Any], prefix: str = "") -> Set[str]:
        sections = set()
        if isinstance(data, dict):
            for key, value in data.items():
                if key.endswith("_comprehensive") or key.endswith("_analysis"):
                    sections.add(key)
                elif isinstance(value, dict):
                    sections.update(extract_sections(value, f"{prefix}.{key}" if prefix else key))
        return sections
    
    analysis["our_sections"] = extract_sections(our_data)
    analysis["reference_sections"] = extract_sections(reference_data)
    
    analysis["missing_sections"] = list(analysis["reference_sections"] - analysis["our_sections"])
    analysis["extra_sections"] = list(analysis["our_sections"] - analysis["reference_sections"])
    analysis["common_sections"] = list(analysis["our_sections"] & analysis["reference_sections"])
    
    return analysis

def generate_improvement_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
    """Generate specific improvement recommendations based on analysis."""
    recommendations = []
    
    # Metrics recommendations
    metrics_analysis = analysis_results.get("metrics_analysis", {})
    if metrics_analysis.get("total_our_metrics", 0) < metrics_analysis.get("total_reference_metrics", 0) * 0.8:
        recommendations.append("🔍 INCREASE METRICS EXTRACTION: Our analysis extracted significantly fewer metrics than reference")
    
    if len(metrics_analysis.get("missing_metrics", [])) > 10:
        recommendations.append("📊 MISSING KEY METRICS: Many important metrics from reference are missing")
    
    if len(metrics_analysis.get("quality_issues", [])) > 5:
        recommendations.append("⚠️ METRICS QUALITY ISSUES: Several metrics have empty or very short values")
    
    # Details recommendations
    details_analysis = analysis_results.get("details_analysis", {})
    if details_analysis.get("total_our_details", 0) < details_analysis.get("total_reference_details", 0) * 0.7:
        recommendations.append("📝 INCREASE DETAILS EXTRACTION: Our analysis extracted significantly fewer details than reference")
    
    if details_analysis.get("avg_our_detail_length", 0) < 100:
        recommendations.append("📏 DETAILS TOO SHORT: Average detail length is much shorter than reference")
    
    if len(details_analysis.get("short_details_our", [])) > 10:
        recommendations.append("🔍 SHORT DETAILS ISSUE: Many details are too short to be meaningful")
    
    # Structure recommendations
    structure_analysis = analysis_results.get("structure_analysis", {})
    if len(structure_analysis.get("missing_sections", [])) > 0:
        recommendations.append("🏗️ MISSING SECTIONS: Some important sections from reference are missing")
    
    # Specific improvements
    if "emissions" not in str(metrics_analysis.get("metric_types_our", {})):
        recommendations.append("🌍 MISSING EMISSIONS METRICS: No emissions-related metrics found")
    
    if "energy" not in str(metrics_analysis.get("metric_types_our", {})):
        recommendations.append("⚡ MISSING ENERGY METRICS: No energy-related metrics found")
    
    return recommendations

def validate_metric_values(our_metrics: Dict[str, Any], reference_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metric values by comparing with reference data."""
    validation_results = {
        "total_metrics_compared": 0,
        "exact_matches": 0,
        "similar_matches": 0,
        "value_mismatches": 0,
        "missing_in_reference": 0,
        "missing_in_ours": 0,
        "exact_matches_list": [],
        "similar_matches_list": [],
        "value_mismatches_list": [],
        "missing_in_reference_list": [],
        "missing_in_ours_list": []
    }
    
    # Normalize metric names for comparison
    our_normalized = normalize_metric_names(our_metrics)
    reference_normalized = normalize_metric_names(reference_metrics)
    
    # Compare metrics
    for metric_name, our_value in our_normalized.items():
        validation_results["total_metrics_compared"] += 1
        
        if metric_name in reference_normalized:
            reference_value = reference_normalized[metric_name]
            
            if our_value == reference_value:
                validation_results["exact_matches"] += 1
                validation_results["exact_matches_list"].append({
                    "metric": metric_name,
                    "our_value": our_value,
                    "reference_value": reference_value
                })
            elif is_similar_value(our_value, reference_value):
                validation_results["similar_matches"] += 1
                validation_results["similar_matches_list"].append({
                    "metric": metric_name,
                    "our_value": our_value,
                    "reference_value": reference_value
                })
            else:
                validation_results["value_mismatches"] += 1
                validation_results["value_mismatches_list"].append({
                    "metric": metric_name,
                    "our_value": our_value,
                    "reference_value": reference_value
                })
        else:
            validation_results["missing_in_reference"] += 1
            validation_results["missing_in_reference_list"].append({
                "metric": metric_name,
                "our_value": our_value
            })
    
    # Find metrics missing in our results
    for metric_name, reference_value in reference_normalized.items():
        if metric_name not in our_normalized:
            validation_results["missing_in_ours"] += 1
            validation_results["missing_in_ours_list"].append({
                "metric": metric_name,
                "reference_value": reference_value
            })
    
    return validation_results

def normalize_metric_names(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize metric names for comparison by removing common variations."""
    normalized = {}
    
    for metric_name, value in metrics.items():
        # Remove common prefixes and suffixes
        normalized_name = metric_name.lower()
        normalized_name = normalized_name.replace('environmental_comprehensive_analysis.', '')
        normalized_name = normalized_name.replace('social_comprehensive_analysis.', '')
        normalized_name = normalized_name.replace('governance_comprehensive_analysis.', '')
        normalized_name = normalized_name.replace('environmental_comprehensive.', '')
        normalized_name = normalized_name.replace('social_comprehensive.', '')
        normalized_name = normalized_name.replace('governance_comprehensive.', '')
        
        # Standardize common variations
        normalized_name = normalized_name.replace('_2022', '_2022')
        normalized_name = normalized_name.replace('_2023', '_2023')
        normalized_name = normalized_name.replace('_2024', '_2024')
        
        normalized[normalized_name] = value
    
    return normalized

def is_similar_value(value1: Any, value2: Any) -> bool:
    """Check if two values are similar (allowing for minor variations)."""
    if value1 == value2:
        return True
    
    # Convert to strings for comparison
    str1 = str(value1).lower().strip()
    str2 = str(value2).lower().strip()
    
    # Handle percentage variations
    if '%' in str1 and '%' in str2:
        try:
            num1 = float(str1.replace('%', ''))
            num2 = float(str2.replace('%', ''))
            return abs(num1 - num2) <= 1.0  # Allow 1% difference
        except:
            pass
    
    # Handle number variations
    try:
        num1 = float(str1.replace(',', '').replace('$', '').replace('M', '').replace('B', ''))
        num2 = float(str2.replace(',', '').replace('$', '').replace('M', '').replace('B', ''))
        return abs(num1 - num2) <= 0.01  # Allow small numerical differences
    except:
        pass
    
    # Handle unit variations
    unit_variations = {
        'mmt co2e': ['million metric tons co2e', 'mmt co2e', 'million tons co2e'],
        'tons': ['tons', 'metric tons', 'tonnes'],
        'million': ['million', 'm', 'mio'],
        'billion': ['billion', 'b', 'bio']
    }
    
    for unit, variations in unit_variations.items():
        if any(var in str1 for var in variations) and any(var in str2 for var in variations):
            # Extract numbers and compare
            import re
            num1_match = re.search(r'(\d+(?:\.\d+)?)', str1)
            num2_match = re.search(r'(\d+(?:\.\d+)?)', str2)
            if num1_match and num2_match:
                try:
                    num1 = float(num1_match.group(1))
                    num2 = float(num2_match.group(1))
                    return abs(num1 - num2) <= 0.01
                except:
                    pass
    
    return False

def main():
    """Main analysis function."""
    print("🔍 COMPREHENSIVE QUALITY ANALYSIS")
    print("="*60)
    
    # Load our analysis results
    our_results_file = Path(__file__).parent / "output" / "analysis_results.json"
    our_results = load_json_file(our_results_file)
    
    if not our_results:
        print("❌ Failed to load our analysis results")
        return
    
    # Load reference Amazon 2022 comprehensive JSON
    reference_file = Path(__file__).parent.parent / "reports-indexing-main" / "json" / "Amazon" / "2022" / "amazon_2022_comprehensive_esg_analysis_clean.json"
    reference_results = load_json_file(reference_file)
    
    if not reference_results:
        print("❌ Failed to load reference Amazon 2022 comprehensive JSON")
        return
    
    print(f"✅ Loaded our analysis results: {len(our_results)} top-level keys")
    print(f"✅ Loaded reference results: {len(reference_results)} top-level keys")
    
    # Extract metrics and details
    print("\n📊 EXTRACTING METRICS AND DETAILS...")
    
    our_metrics = extract_metrics_from_section(our_results)
    reference_metrics = extract_metrics_from_section(reference_results)
    
    our_details = extract_details_from_section(our_results)
    reference_details = extract_details_from_section(reference_results)
    
    print(f"📊 Our metrics: {len(our_metrics)}")
    print(f"📊 Reference metrics: {len(reference_metrics)}")
    print(f"📝 Our details: {len(our_details)}")
    print(f"📝 Reference details: {len(reference_details)}")
    
    # Perform comprehensive analysis
    print("\n🔍 ANALYZING QUALITY...")
    
    metrics_analysis = analyze_metrics_quality(our_metrics, reference_metrics)
    details_analysis = analyze_details_quality(our_details, reference_details)
    structure_analysis = analyze_structure_quality(our_results, reference_results)
    
    # Add value validation
    print("\n🔍 VALIDATING METRIC VALUES...")
    value_validation = validate_metric_values(our_metrics, reference_metrics)
    
    # Compile results
    analysis_results = {
        "metrics_analysis": metrics_analysis,
        "details_analysis": details_analysis,
        "structure_analysis": structure_analysis,
        "value_validation": value_validation,
        "summary": {
            "overall_metrics_coverage": len(our_metrics) / len(reference_metrics) if reference_metrics else 0,
            "overall_details_coverage": len(our_details) / len(reference_details) if reference_details else 0,
            "value_accuracy": (value_validation["exact_matches"] + value_validation["similar_matches"]) / value_validation["total_metrics_compared"] if value_validation["total_metrics_compared"] > 0 else 0,
            "quality_score": 0  # Will be calculated
        }
    }
    
    # Calculate quality score with value validation
    quality_score = 0
    if reference_metrics:
        quality_score += (len(our_metrics) / len(reference_metrics)) * 35  # 35% weight for metrics coverage
    if reference_details:
        quality_score += (len(our_details) / len(reference_details)) * 25  # 25% weight for details coverage
    if reference_results:
        quality_score += (len(structure_analysis["common_sections"]) / len(structure_analysis["reference_sections"])) * 20  # 20% weight for structure
    if value_validation["total_metrics_compared"] > 0:
        value_accuracy = (value_validation["exact_matches"] + value_validation["similar_matches"]) / value_validation["total_metrics_compared"]
        quality_score += value_accuracy * 20  # 20% weight for value accuracy
    
    analysis_results["summary"]["quality_score"] = quality_score
    
    # Generate recommendations
    recommendations = generate_improvement_recommendations(analysis_results)
    
    # Display results
    print("\n" + "="*60)
    print("📊 QUALITY ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n🎯 OVERALL QUALITY SCORE: {quality_score:.1f}/100")
    print(f"📊 Metrics Coverage: {analysis_results['summary']['overall_metrics_coverage']:.1%}")
    print(f"📝 Details Coverage: {analysis_results['summary']['overall_details_coverage']:.1%}")
    print(f"✅ Value Accuracy: {analysis_results['summary']['value_accuracy']:.1%}")
    
    print(f"\n📊 METRICS ANALYSIS:")
    print(f"   - Our metrics: {metrics_analysis['total_our_metrics']}")
    print(f"   - Reference metrics: {metrics_analysis['total_reference_metrics']}")
    print(f"   - Missing metrics: {len(metrics_analysis['missing_metrics'])}")
    print(f"   - Extra metrics: {len(metrics_analysis['extra_metrics'])}")
    print(f"   - Common metrics: {len(metrics_analysis['common_metrics'])}")
    
    print(f"\n🔍 VALUE VALIDATION:")
    print(f"   - Total metrics compared: {value_validation['total_metrics_compared']}")
    print(f"   - Exact matches: {value_validation['exact_matches']}")
    print(f"   - Similar matches: {value_validation['similar_matches']}")
    print(f"   - Value mismatches: {value_validation['value_mismatches']}")
    print(f"   - Missing in reference: {value_validation['missing_in_reference']}")
    print(f"   - Missing in ours: {value_validation['missing_in_ours']}")
    
    print(f"\n📝 DETAILS ANALYSIS:")
    print(f"   - Our details: {details_analysis['total_our_details']}")
    print(f"   - Reference details: {details_analysis['total_reference_details']}")
    print(f"   - Avg our detail length: {details_analysis['avg_our_detail_length']:.1f} chars")
    print(f"   - Avg reference detail length: {details_analysis['avg_reference_detail_length']:.1f} chars")
    
    print(f"\n🏗️ STRUCTURE ANALYSIS:")
    print(f"   - Our sections: {len(structure_analysis['our_sections'])}")
    print(f"   - Reference sections: {len(structure_analysis['reference_sections'])}")
    print(f"   - Missing sections: {len(structure_analysis['missing_sections'])}")
    print(f"   - Extra sections: {len(structure_analysis['extra_sections'])}")
    
    # Show metric types comparison
    print(f"\n📈 METRIC TYPES COMPARISON:")
    print("   Our metrics by type:")
    for metric_type, count in metrics_analysis['metric_types_our'].most_common():
        print(f"     - {metric_type}: {count}")
    
    print("   Reference metrics by type:")
    for metric_type, count in metrics_analysis['metric_types_reference'].most_common():
        print(f"     - {metric_type}: {count}")
    
    # Show quality issues
    if metrics_analysis['quality_issues']:
        print(f"\n⚠️ METRICS QUALITY ISSUES:")
        for issue in metrics_analysis['quality_issues'][:10]:  # Show first 10
            print(f"   - {issue}")
        if len(metrics_analysis['quality_issues']) > 10:
            print(f"   ... and {len(metrics_analysis['quality_issues']) - 10} more")
    
    if details_analysis['quality_issues']:
        print(f"\n⚠️ DETAILS QUALITY ISSUES:")
        for issue in details_analysis['quality_issues'][:10]:  # Show first 10
            print(f"   - {issue}")
        if len(details_analysis['quality_issues']) > 10:
            print(f"   ... and {len(details_analysis['quality_issues']) - 10} more")
    
    # Show recommendations
    print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")
    for recommendation in recommendations:
        print(f"   {recommendation}")
    
    # Save detailed analysis
    output_file = Path(__file__).parent / "output" / "quality_analysis_report.json"
    
    # Convert sets to lists for JSON serialization
    serializable_results = json.loads(json.dumps(analysis_results, default=lambda x: list(x) if isinstance(x, set) else x))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")
    
    # Show sample missing metrics
    if metrics_analysis['missing_metrics']:
        print(f"\n🔍 SAMPLE MISSING METRICS (first 10):")
        for metric in metrics_analysis['missing_metrics'][:10]:
            print(f"   - {metric}")
    
    # Show sample missing sections
    if structure_analysis['missing_sections']:
        print(f"\n🏗️ MISSING SECTIONS:")
        for section in structure_analysis['missing_sections']:
            print(f"   - {section}")

if __name__ == "__main__":
    main() 