#!/usr/bin/env python3
"""
Enhanced Convert Comprehensive ESG Analysis to Dashboard Format
Converts any company/year analysis to dashboard format with integrated metric name enhancement and category generation
PRESERVES ORIGINAL VALUES AND UNITS FROM COMPREHENSIVE JSON - NO UNIT CONVERSION
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the API client
from direct_api_client import make_direct_api_call

def clean_metric_values(metrics):
    """Clean metric values by properly separating numeric values from units - PRESERVE UNIT INTEGRITY"""
    import re
    
    cleaned_metrics = []
    total_metrics = len(metrics)
    
    print(f"🧹 Processing {total_metrics} metrics - SEPARATING VALUES AND UNITS...")
    
    for i, metric in enumerate(metrics):
        if i % 50 == 0:  # Show progress every 50 metrics
            print(f"   Progress: {i}/{total_metrics} metrics processed")
            
        cleaned_metric = metric.copy()
        value = metric.get('value', '')
        metric_name = metric.get('metric_name', '')
        
        # CRITICAL FIX: Properly separate numeric values from units
        # The comprehensive JSON has values like "2.1-2.3 gigatons"
        # We need to extract: value="2.1-2.3", unit="gigatons"
        
        if isinstance(value, str):
            # Store the original value for reference
            cleaned_metric['original_value_with_unit'] = value
            
            # Extract numeric value and unit using regex
            # Handle various formats: "2.1-2.3 gigatons", "717,000 tons", "85%", etc.
            
            # Pattern for numeric values (including ranges, commas, decimals)
            numeric_pattern = r'(\d+(?:,\d+)*(?:\.\d+)?(?:-\d+(?:,\d+)*(?:\.\d+)?)?)'
            
            # Find the numeric part
            numeric_match = re.search(numeric_pattern, value)
            if numeric_match:
                numeric_value = numeric_match.group(1)
                # Remove commas from numeric value for consistency
                numeric_value = numeric_value.replace(',', '')
                cleaned_metric['value'] = numeric_value
                
                # Extract unit from the remaining part
                unit_part = value.replace(numeric_match.group(0), '').strip()
                
                # Clean up unit part
                if unit_part:
                    # Remove common separators and clean up
                    unit_part = re.sub(r'^[\s,.-]+', '', unit_part)  # Remove leading separators
                    unit_part = re.sub(r'[\s,.-]+$', '', unit_part)  # Remove trailing separators
                    
                    if unit_part:
                        cleaned_metric['unit'] = unit_part
                    else:
                        cleaned_metric['unit'] = None
                else:
                    cleaned_metric['unit'] = None
            else:
                # No numeric value found, keep original
                cleaned_metric['value'] = value
                cleaned_metric['unit'] = None
            
            cleaned_metric['unit_conversion_applied'] = False  # No conversion applied
        
        cleaned_metrics.append(cleaned_metric)
    
    print(f"   Progress: {total_metrics}/{total_metrics} metrics processed - Complete!")
    print(f"   ✅ PROPERLY SEPARATED VALUES AND UNITS WHILE PRESERVING INTEGRITY")
    return cleaned_metrics

def convert_comprehensive_to_dashboard_enhanced(input_file=None, output_file=None, company="Amazon", year="2020"):
    """Convert comprehensive ESG analysis to dashboard format with enhanced metric names and categories"""
    
    # Require input_file and output_file to be provided
    if not input_file or not output_file:
        print("❌ Error: input_file and output_file must be provided")
        return None
    
    print(f"Converting {input_file} to enhanced dashboard format...")
    print(f"Company: {company}, Year: {year}")
    
    # Load the comprehensive ESG analysis
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        return None
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return None
    
    # Extract metrics from the analysis (same logic as original)
    metrics = extract_metrics_from_analysis(analysis_data, company, year)
    
    if not metrics:
        print("❌ No metrics extracted from analysis")
        return None
    
    print(f"📊 Extracted {len(metrics)} metrics from analysis")
    
    # Step 1: Create basic dashboard format
    dashboard_data = {
        "company": company,
        "year": year,
        "file_path": str(input_file),
        "metrics": metrics
    }
    
    # Step 2: Combined processing - enhance names, generate categories, and analyze importance in one go
    print(f"🚀 Step 2: Combined processing (enhance names, categories, and importance)...")
    processed_metrics = process_all_metrics_combined(metrics, company, year)
    dashboard_data["metrics"] = processed_metrics
    
    # Step 3: Clean metric values by removing embedded units
    print(f"🧹 Step 3: Cleaning metric values...")
    cleaned_metrics = clean_metric_values(processed_metrics)
    dashboard_data["metrics"] = cleaned_metrics
    
    # Step 4: Save the enhanced dashboard data
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Enhanced dashboard data saved to: {output_file}")
        print(f"📊 Final metrics count: {len(cleaned_metrics)}")
        return output_file
    except Exception as e:
        print(f"❌ Error saving dashboard data: {e}")
        return None

def extract_metrics_from_analysis(analysis_data, company, year):
    """Extract ALL metrics from comprehensive analysis using recursive search - NO RESTRICTIONS"""
    metrics = []
    
    def extract_metrics_recursive(data, path="", parent_details=None):
        """Recursively extract ALL metrics from nested structures without restrictions"""
        if isinstance(data, dict):
            # Check if this level has details
            current_details = data.get("details", [])
            if current_details:
                parent_details = current_details
            
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if key == "metrics" and isinstance(value, dict):
                    # Found a metrics section - extract ALL metrics
                    for metric_name, metric_value in value.items():
                        if metric_value and metric_value != {} and metric_value != []:  # Only add if value exists and is not empty
                            # Determine category based on path
                            category = determine_category_from_path(current_path)
                            subcategory = determine_subcategory_from_path(current_path)
                            
                            # Process details - replace underscores with spaces
                            processed_details = []
                            if parent_details:
                                for detail in parent_details:
                                    if isinstance(detail, str):
                                        # Replace underscores with spaces
                                        processed_detail = detail.replace("_", " ")
                                        processed_details.append(processed_detail)
                            
                            # CRITICAL FIX: Preserve the original metric_value exactly as it appears in comprehensive JSON
                            # Do NOT call determine_unit_from_metric_name() which overrides the original units
                            # The comprehensive JSON already has correct values with units like "2.1-2.3 gigatons"
                            metrics.append({
                                "metric_name": f"{metric_name}",
                                "value": metric_value,  # Keep original value exactly as is
                                "unit": None,  # Don't override with generic unit - preserve original
                                "description": f"Metric from {current_path}",
                                "category": category,
                                "type": determine_type_from_category(category),
                                "area": determine_area_from_category(category),
                                "subcategory": subcategory,
                                "importance": "Medium",  # Will be enhanced by LLM later
                                "details": processed_details
                            })
                else:
                    # Continue recursive search in ALL nested structures
                    extract_metrics_recursive(value, current_path, parent_details)
    
    # Start recursive extraction from the main analysis sections
    for section in ["environmental_comprehensive_analysis", "social_comprehensive_analysis", "governance_comprehensive_analysis"]:
        if section in analysis_data:
            extract_metrics_recursive(analysis_data[section])
    
    return metrics

def determine_category_from_path(path):
    """Determine ESG category from the path in the data structure"""
    path_lower = path.lower()
    
    if "environmental" in path_lower or "emissions" in path_lower or "energy" in path_lower or "water" in path_lower or "waste" in path_lower or "carbon" in path_lower:
        return "E - environmental"
    elif "social" in path_lower or "human" in path_lower or "labor" in path_lower or "community" in path_lower or "employee" in path_lower:
        return "S - social"
    elif "governance" in path_lower or "board" in path_lower or "ethics" in path_lower or "compliance" in path_lower:
        return "G - governance"
    else:
        return "E - environmental"  # Default to environmental

def determine_subcategory_from_path(path):
    """Determine subcategory from the path"""
    path_lower = path.lower()
    
    if "emissions" in path_lower or "scope" in path_lower:
        return "Carbon Emissions"
    elif "energy" in path_lower or "renewable" in path_lower:
        return "Energy"
    elif "water" in path_lower:
        return "Water"
    elif "waste" in path_lower or "packaging" in path_lower:
        return "Waste"
    elif "transportation" in path_lower or "vehicles" in path_lower:
        return "Transportation"
    elif "buildings" in path_lower:
        return "Buildings"
    elif "supply_chain" in path_lower:
        return "Supply Chain"
    elif "employee" in path_lower or "workforce" in path_lower:
        return "Employee"
    elif "community" in path_lower:
        return "Community"
    elif "board" in path_lower:
        return "Board"
    elif "ethics" in path_lower:
        return "Ethics"
    else:
        return "Other"

def determine_type_from_category(category):
    """Determine metric type from category"""
    if category.startswith("E"):
        return "environmental"
    elif category.startswith("S"):
        return "social"
    elif category.startswith("G"):
        return "governance"
    else:
        return "environmental"

def determine_area_from_category(category):
    """Determine area from category"""
    if category.startswith("E"):
        return "E"
    elif category.startswith("S"):
        return "S"
    elif category.startswith("G"):
        return "G"
    else:
        return "E"

def enhance_metric_names_batch(metrics, company, year):
    """Enhance metric names using LLM (extracted from enhance_metric_names.py)"""
    print(f"  🔧 Enhancing {len(metrics)} metric names...")
    
    # Process metrics in batches
    enhanced_metrics = []
    batch_size = 10
    
    for i in range(0, len(metrics), batch_size):
        batch = metrics[i:i + batch_size]
        print(f"    Processing batch {i//batch_size + 1}/{(len(metrics) + batch_size - 1)//batch_size}")
        
        enhanced_batch = enhance_metric_batch(batch, company, year)
        enhanced_metrics.extend(enhanced_batch)
    
    return enhanced_metrics

def enhance_metric_batch(metrics_batch, company, year):
    """Enhance a batch of metrics using LLM"""
    
    # Create prompt for LLM
    prompt_content = f"""
You are an expert ESG analyst tasked with converting raw metric names into clear, direct, and meaningful descriptions.

COMPANY: {company}
YEAR: {year}

TASK: Convert the following raw metric names into clear, professional, and meaningful descriptions that would be suitable for a dashboard display.

GUIDELINES:
1. Make names clear and understandable to non-technical audiences
2. Keep them concise but descriptive
3. Use professional ESG terminology
4. Maintain the original meaning and context
5. Remove technical jargon and abbreviations where possible
6. Make them consistent with ESG reporting standards

EXAMPLES:
- "Carbon Emissions Scope 1 - emissions_from_direct_operations_scope_1_2019" → "Carbon Emissions Scope 1 (2019)"
- "Employee - total_employees" → "Total Employees"
- "Board - independent_directors_percentage" → "Board Independence"

RAW METRIC NAMES TO CONVERT:
{chr(10).join([f"- {metric.get('metric_name', 'Unknown')}" for metric in metrics_batch])}

Provide the enhanced metric names in JSON format:
{{
  "enhanced_metrics": [
    {{
      "original_name": "original_metric_name",
      "enhanced_name": "enhanced_metric_name"
    }}
  ]
}}
"""
    
    try:
        # Create messages in the correct format
        messages = [
            {"role": "system", "content": "You are an expert ESG analyst."},
            {"role": "user", "content": prompt_content}
        ]
        
        # Make API call
        response = make_direct_api_call(messages, max_tokens=2000)
        
        if response and 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Update metric names
                enhanced_metrics = []
                for metric in metrics_batch:
                    enhanced_metric = metric.copy()
                    
                    # Find corresponding enhanced name
                    for enhanced_item in result.get('enhanced_metrics', []):
                        if enhanced_item.get('original_name') == metric.get('metric_name'):
                            enhanced_metric['metric_name'] = enhanced_item.get('enhanced_name', metric.get('metric_name'))
                            break
                    
                    enhanced_metrics.append(enhanced_metric)
                
                return enhanced_metrics
        
        # Fallback: return original metrics
        print(f"    ⚠️ LLM enhancement failed, using original names")
        return metrics_batch
        
    except Exception as e:
        print(f"    ⚠️ Error in metric enhancement: {e}")
        return metrics_batch

def generate_esg_categories_batch(metrics, company, year):
    """Generate ESG categories using LLM (extracted from generate_esg_categories.py)"""
    print(f"  🏷️ Generating categories for {len(metrics)} metrics...")
    
    # Process metrics in batches
    categorized_metrics = []
    batch_size = 10
    
    for i in range(0, len(metrics), batch_size):
        batch = metrics[i:i + batch_size]
        print(f"    Processing batch {i//batch_size + 1}/{(len(metrics) + batch_size - 1)//batch_size}")
        
        categorized_batch = categorize_metric_batch(batch, company, year)
        categorized_metrics.extend(categorized_batch)
    
    return categorized_metrics

def categorize_metric_batch(metrics_batch, company, year):
    """Generate categories for a batch of metrics using LLM"""
    
    # Create prompt for LLM
    prompt_content = f"""
You are an expert ESG analyst tasked with categorizing ESG metrics into detailed categories.

COMPANY: {company}
YEAR: {year}

TASK: Categorize the following ESG metrics into detailed, specific categories that would be useful for dashboard filtering and analysis.

CATEGORY GUIDELINES:
- Use the format "ESG Area - Specific Category"
- ESG Areas: E (Environmental), S (Social), G (Governance)
- Be specific and descriptive
- Examples: "E - carbon emissions", "S - employee development", "G - board governance"

METRICS TO CATEGORIZE:
{chr(10).join([f"- {metric.get('metric_name', 'Unknown')} (Current: {metric.get('category', 'None')})" for metric in metrics_batch])}

Provide the categories in JSON format:
{{
  "categorized_metrics": [
    {{
      "metric_name": "metric_name",
      "category": "E - specific_category"
    }}
  ]
}}
"""
    
    try:
        # Create messages in the correct format
        messages = [
            {"role": "system", "content": "You are an expert ESG analyst."},
            {"role": "user", "content": prompt_content}
        ]
        
        # Make API call
        response = make_direct_api_call(messages, max_tokens=2000)
        
        if response and 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Update metric categories
                categorized_metrics = []
                for metric in metrics_batch:
                    categorized_metric = metric.copy()
                    
                    # Find corresponding category
                    for categorized_item in result.get('categorized_metrics', []):
                        if categorized_item.get('metric_name') == metric.get('metric_name'):
                            categorized_metric['category'] = categorized_item.get('category', metric.get('category', ''))
                            break
                    
                    categorized_metrics.append(categorized_metric)
                
                return categorized_metrics
        
        # Fallback: return original metrics
        print(f"    ⚠️ LLM categorization failed, using original categories")
        return metrics_batch
        
    except Exception as e:
        print(f"    ⚠️ Error in metric categorization: {e}")
        return metrics_batch

def generate_importance_analysis_batch(metrics, company, year):
    """Generate LLM-powered importance analysis for metrics in batches"""
    print(f"🔍 Generating importance analysis for {len(metrics)} metrics...")
    
    # Process in batches of 3 (smaller batches for better reliability)
    batch_size = 3
    enhanced_metrics = []
    
    for i in range(0, len(metrics), batch_size):
        batch = metrics[i:i + batch_size]
        print(f"📊 Processing importance analysis batch {i//batch_size + 1}/{(len(metrics) + batch_size - 1)//batch_size}")
        
        try:
            enhanced_batch = analyze_importance_batch(batch, company, year)
            enhanced_metrics.extend(enhanced_batch)
        except Exception as e:
            print(f"⚠️ Error processing batch {i//batch_size + 1}: {e}")
            # Add original metrics with default importance for this batch
            for metric in batch:
                enhanced_metric = metric.copy()
                enhanced_metric['importance'] = "Medium"
                enhanced_metric['importance_reasoning'] = f"Batch processing failed: {str(e)[:50]}"
                enhanced_metrics.append(enhanced_metric)
    
    print(f"✅ Importance analysis completed for {len(enhanced_metrics)} metrics")
    return enhanced_metrics

def analyze_importance_batch(metrics_batch, company, year):
    """Analyze importance for a batch of metrics using LLM"""
    
    # Prepare metrics for LLM analysis
    metrics_text = []
    for i, metric in enumerate(metrics_batch):
        metric_info = f"Metric {i+1}: {metric['metric_name']}\n"
        metric_info += f"Value: {metric['value']} {metric.get('unit', '')}\n"
        metric_info += f"Category: {metric['category']}\n"
        metric_info += f"Subcategory: {metric['subcategory']}\n"
        if metric.get('details'):
            metric_info += f"Context: {' '.join(metric['details'][:2])}\n"  # Use first 2 details for context
        metric_info += "---\n"
        metrics_text.append(metric_info)
    
    combined_text = "\n".join(metrics_text)
    
    # LLM prompt for importance analysis
    prompt = f"""You are an ESG analyst evaluating the importance of sustainability metrics for {company} in {year}.

For each metric below, analyze its importance based on:
1. **Strategic Impact**: How critical is this metric to {company}'s sustainability strategy?
2. **Stakeholder Interest**: How important is this to investors, customers, employees, regulators?
3. **ANALYZE IMPORTANCE USING DOUBLE MATERIALITY ASSESSMENT**: Rate as High/Medium/Low based on comprehensive double materiality evaluation:

   **FINANCIAL MATERIALITY (Impact on Company Value):**
   - HIGH: Direct impact on financial performance, regulatory compliance, market position, or investor decisions
   - MEDIUM: Moderate impact on operations, reputation, or stakeholder relationships
   - LOW: Minimal direct financial impact or primarily operational in nature

   **IMPACT MATERIALITY (Impact on Society/Environment):**
   - HIGH: Significant environmental damage, human rights violations, or major social/environmental benefits
   - MEDIUM: Moderate environmental or social impact, local community effects
   - LOW: Minimal environmental or social impact, primarily internal operational matters

   **FINAL IMPORTANCE RATING:**
   - HIGH: High in either Financial OR Impact materiality (or both)
   - MEDIUM: Medium in both Financial AND Impact materiality, or High in one and Low in the other
   - LOW: Low in both Financial AND Impact materiality

   **REASONING FORMAT:** "Financial: [High/Medium/Low] - [brief financial impact reasoning] | Impact: [High/Medium/Low] - [brief environmental/social impact reasoning]"

Use the context details provided to make informed decisions about categorization and double materiality assessment.

Metrics to analyze:
{combined_text}

Provide your analysis in this exact format:
Metric 1: [High/Medium/Low] - [brief reasoning]
Metric 2: [High/Medium/Low] - [brief reasoning]
...
Metric {len(metrics_batch)}: [High/Medium/Low] - [brief reasoning]

Focus on practical business impact and stakeholder relevance."""

    # Initialize enhanced_batch with default values
    enhanced_batch = []
    for metric in metrics_batch:
        enhanced_metric = metric.copy()
        enhanced_metric['importance'] = "Medium"
        enhanced_metric['importance_reasoning'] = "Analysis unavailable"
        enhanced_batch.append(enhanced_metric)

    try:
        # Make API call
        response = make_direct_api_call([
            {"role": "system", "content": "You are an expert ESG analyst with deep knowledge of sustainability metrics and corporate reporting."},
            {"role": "user", "content": prompt}
        ])
        
        if response and "content" in response:
            analysis_text = response["content"]
            print(f"🔍 LLM Response: {analysis_text[:300]}...")  # Debug: show first 300 chars
            
            # Parse the response to extract importance levels
            for i, metric in enumerate(metrics_batch):
                # Try to extract importance from the response - try multiple patterns
                patterns = [
                    f"Metric {i+1}:",
                    f"Metric {i+1} :",
                    f"Metric {i+1}.",
                    f"Metric {i+1} -",
                    f"Metric {i+1}-"
                ]
                
                found = False
                for pattern in patterns:
                    if pattern in analysis_text:
                        # Extract the line containing this metric
                        lines = analysis_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith(pattern):
                                # Parse: "Metric X: High - reasoning" or "Metric X: High"
                                try:
                                    # Remove the pattern from the line
                                    remaining = line[len(pattern):].strip()
                                    
                                    # Look for importance level
                                    if ' - ' in remaining:
                                        importance_part, reasoning = remaining.split(' - ', 1)
                                    elif ':' in remaining:
                                        importance_part, reasoning = remaining.split(':', 1)
                                    else:
                                        importance_part = remaining
                                        reasoning = ""
                                    
                                    importance_part = importance_part.strip()
                                    
                                    # Validate importance level
                                    if importance_part.lower() in ['high', 'medium', 'low']:
                                        enhanced_batch[i]['importance'] = importance_part.capitalize()
                                        enhanced_batch[i]['importance_reasoning'] = reasoning.strip()
                                        found = True
                                        break
                                except Exception as parse_error:
                                    print(f"⚠️ Parse error for {pattern}: {parse_error}")
                                    continue
                        
                        if found:
                            break
                
                if not found:
                    # Try to find any importance level in the response
                    if 'high' in analysis_text.lower():
                        enhanced_batch[i]['importance'] = "High"
                        enhanced_batch[i]['importance_reasoning'] = "High importance based on analysis"
                    elif 'low' in analysis_text.lower():
                        enhanced_batch[i]['importance'] = "Low"
                        enhanced_batch[i]['importance_reasoning'] = "Low importance based on analysis"
                    else:
                        enhanced_batch[i]['importance'] = "Medium"
                        enhanced_batch[i]['importance_reasoning'] = "Medium importance - default assessment"
            
    except Exception as e:
        print(f"⚠️ Error in importance analysis: {e}")
        # Update reasoning to show the error
        for i in range(len(enhanced_batch)):
            enhanced_batch[i]['importance_reasoning'] = f"Analysis failed: {str(e)[:100]}"
    
    return enhanced_batch

def process_metrics_combined_batch(metrics_batch, company, year):
    """Process metrics in a single batch: enhance names, generate categories, and analyze importance"""
    
    # Prepare metrics for combined LLM analysis
    metrics_text = []
    for i, metric in enumerate(metrics_batch):
        metric_info = f"Metric {i+1}:\n"
        metric_info += f"Original Name: {metric['metric_name']}\n"
        metric_info += f"Value: {metric['value']} {metric.get('unit', '')}\n"
        metric_info += f"Category: {metric['category']}\n"
        metric_info += f"Subcategory: {metric['subcategory']}\n"
        # Include details for better context
        if metric.get('details') and len(metric['details']) > 0:
            metric_info += f"Context Details:\n"
            for j, detail in enumerate(metric['details'][:3]):  # Use up to 3 details
                metric_info += f"  - {detail}\n"
        metric_info += "---\n"
        metrics_text.append(metric_info)
    
    combined_text = "\n".join(metrics_text)
    
    # Combined LLM prompt for all processing
    prompt = f"""You are an expert ESG analyst processing sustainability metrics for {company} in {year}.

For each metric below, perform THREE tasks:

1. **ENHANCE METRIC NAME**: Create a clear, professional metric name that accurately describes what is being measured
2. **GENERATE ESG CATEGORY**: Assign one of these categories with SPECIFIC subcategories:
   - E - Environmental: Carbon Emissions, Energy, Energy Efficiency, Water Management, Waste Management, Biodiversity, Climate Adaptation, Renewable Energy, Transportation, Buildings, Supply Chain Environmental Impact
   - S - Social: Employee Health & Safety, Community Engagement, Human Rights, Labor Standards, Diversity & Inclusion, Education & Training, Health & Wellness, Economic Development, Food Security, Digital Inclusion
   - G - Governance: Board Diversity, Ethics & Compliance, Risk Management, Transparency, Stakeholder Engagement, Executive Compensation, Anti-Corruption, Data Privacy, Cybersecurity, Regulatory Compliance
3. **ANALYZE IMPORTANCE USING DOUBLE MATERIALITY ASSESSMENT**: Rate as High/Medium/Low based on comprehensive double materiality evaluation:

   **FINANCIAL MATERIALITY (Impact on Company Value):**
   - HIGH: Direct impact on financial performance, regulatory compliance, market position, or investor decisions
   - MEDIUM: Moderate impact on operations, reputation, or stakeholder relationships
   - LOW: Minimal direct financial impact or primarily operational in nature

   **IMPACT MATERIALITY (Impact on Society/Environment):**
   - HIGH: Significant environmental damage, human rights violations, or major social/environmental benefits
   - MEDIUM: Moderate environmental or social impact, local community effects
   - LOW: Minimal environmental or social impact, primarily internal operational matters

   **FINAL IMPORTANCE RATING:**
   - HIGH: High in either Financial OR Impact materiality (or both)
   - MEDIUM: Medium in both Financial AND Impact materiality, or High in one and Low in the other
   - LOW: Low in both Financial AND Impact materiality

   **REASONING FORMAT:** "Financial: [High/Medium/Low] - [brief financial impact reasoning] | Impact: [High/Medium/Low] - [brief environmental/social impact reasoning]"

Use the context details provided to make informed decisions about categorization and double materiality assessment.

Metrics to process:
{combined_text}

CRITICAL FORMAT REQUIREMENTS:
- Use EXACTLY this format for each metric - NO VARIATIONS ALLOWED
- NO markdown formatting (no **, ###, or any other formatting)
- NO bold text, no headers, no special characters
- Use ONLY plain text with the exact structure shown below

Provide your analysis in this EXACT format (copy this structure exactly):

Metric 1:
- Enhanced Name: [clear, professional name]
- ESG Category: [E/S/G] - [specific subcategory from the list above]
- Importance: [High/Medium/Low] - [brief reasoning]

Metric 2:
- Enhanced Name: [clear, professional name]
- ESG Category: [E/S/G] - [specific subcategory from the list above]
- Importance: [High/Medium/Low] - [brief reasoning]

...
Metric {len(metrics_batch)}:
- Enhanced Name: [clear, professional name]
- ESG Category: [E/S/G] - [specific subcategory from the list above]
- Importance: [High/Medium/Low] - [brief reasoning]

FORMAT RULES:
1. Start each metric with "Metric X:" (no bold, no headers, no special characters)
2. Use "- " for each field (Enhanced Name, ESG Category, Importance)
3. Use ":" after each field name
4. NO markdown formatting anywhere
5. NO variations in format - use exactly as shown above

Focus on accuracy, clarity, and practical business relevance. Use the specific subcategories listed above."""

    # Initialize enhanced_batch with original values (including details)
    enhanced_batch = []
    for metric in metrics_batch:
        enhanced_metric = metric.copy()
        # Ensure details are preserved
        if 'details' not in enhanced_metric:
            enhanced_metric['details'] = []
        enhanced_batch.append(enhanced_metric)

    try:
        # Make API call
        response = make_direct_api_call([
            {"role": "system", "content": "You are an expert ESG analyst with deep knowledge of sustainability metrics, corporate reporting, ESG frameworks, and double materiality assessment methodologies. You specialize in evaluating both financial materiality (impact on company value) and impact materiality (impact on society/environment) according to international ESG standards."},
            {"role": "user", "content": prompt}
        ])
        
        if response and "choices" in response and len(response["choices"]) > 0:
            analysis_text = response["choices"][0]["message"]["content"]
            print(f"🔍 Combined LLM Response: {analysis_text[:400]}...")  # Debug: show first 400 chars
            
            # Add more detailed debug for first batch only
            if len(metrics_batch) <= 3:  # Only for small batches to avoid spam
                print(f"🔍 Full LLM Response for batch:")
                print(analysis_text)
                print("🔍 End of LLM Response")
            
            # Parse the response to extract all information
            for metric_idx, metric in enumerate(metrics_batch):
                # Look for the specific metric in the response - now only one format expected
                metric_pattern = f"Metric {metric_idx + 1}:"
                
                metric_found = False
                
                # Check if the pattern exists in the response
                if metric_pattern in analysis_text:
                    metric_found = True
                
                if metric_found:
                    # Extract the section for this metric
                    lines = analysis_text.split('\n')
                    metric_section = []
                    in_metric_section = False
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith(metric_pattern):
                            in_metric_section = True
                            continue
                        elif line.startswith(f"Metric {metric_idx + 2}:"):
                            break
                        elif in_metric_section and line:
                            metric_section.append(line)
                    
                    # Debug: Print metric section for first few metrics
                    if metric_idx < 3:  # Only debug first 3 metrics to avoid spam
                        print(f"🔍 Debug - Metric {metric_idx + 1} section lines: {len(metric_section)}")
                        for i, section_line in enumerate(metric_section):
                            print(f"  {i+1}: '{section_line}'")
                    
                    # Parse the metric section
                    enhanced_name = metric['metric_name']  # Default to original
                    esg_category = metric['category']  # Default to original
                    importance = "Medium"  # Default
                    reasoning = "Analysis unavailable"
                    
                    for line in metric_section:
                        line_lower = line.lower()
                        
                        # Parse Enhanced Name
                        if "enhanced name:" in line_lower:
                            try:
                                enhanced_name = line.split(":", 1)[1].strip()
                                if metric_idx < 3:  # Debug output
                                    print(f"🔍 Debug - Enhanced name found: '{enhanced_name}'")
                            except Exception as e:
                                if metric_idx < 3:  # Debug output
                                    print(f"🔍 Debug - Error parsing enhanced name: {e}")
                                pass
                        
                        # Parse ESG Category
                        elif "esg category:" in line_lower:
                            try:
                                category_part = line.split(":", 1)[1].strip()
                                # Use the full category including subcategory
                                if category_part.startswith("E"):
                                    esg_category = category_part
                                elif category_part.startswith("S"):
                                    esg_category = category_part
                                elif category_part.startswith("G"):
                                    esg_category = category_part
                                else:
                                    # Fallback to main category if format is unexpected
                                    if "environmental" in category_part.lower():
                                        esg_category = "E - environmental"
                                    elif "social" in category_part.lower():
                                        esg_category = "S - social"
                                    elif "governance" in category_part.lower():
                                        esg_category = "G - governance"
                            except:
                                pass
                        
                        # Parse Importance
                        elif "importance:" in line_lower:
                            try:
                                importance_part = line.split(":", 1)[1].strip()
                                print(f"🔍 Debug - Raw importance line: '{line}'")
                                print(f"🔍 Debug - Importance part: '{importance_part}'")
                                
                                if " - " in importance_part:
                                    importance_level, reasoning = importance_part.split(" - ", 1)
                                    print(f"🔍 Debug - Split result: level='{importance_level}', reasoning='{reasoning}'")
                                else:
                                    importance_level = importance_part
                                    reasoning = "Based on analysis"
                                    print(f"🔍 Debug - No split, using default reasoning")
                                
                                if importance_level.lower() in ['high', 'medium', 'low']:
                                    importance = importance_level.capitalize()
                                    reasoning = reasoning.strip()
                                    print(f"🔍 Debug - Final: importance='{importance}', reasoning='{reasoning}'")
                                else:
                                    print(f"🔍 Debug - Invalid importance level: '{importance_level}'")
                            except Exception as parse_error:
                                print(f"🔍 Debug - Error parsing importance: {parse_error}")
                                pass
                    
                    # Update the enhanced metric (preserve details)
                    enhanced_batch[metric_idx]['metric_name'] = enhanced_name
                    enhanced_batch[metric_idx]['category'] = esg_category
                    enhanced_batch[metric_idx]['type'] = determine_type_from_category(esg_category)
                    enhanced_batch[metric_idx]['area'] = determine_area_from_category(esg_category)
                    enhanced_batch[metric_idx]['importance'] = importance
                    enhanced_batch[metric_idx]['importance_reasoning'] = reasoning
                    # Details are already preserved from the original metric
                else:
                    # Debug: Show what patterns were not found
                    if metric_idx < 3:  # Only debug first 3 metrics to avoid spam
                        print(f"🔍 Debug - Metric {metric_idx + 1} pattern NOT found!")
                        print(f"🔍 Debug - Looking for pattern: {metric_pattern}")
                        # Find all metric patterns in the response
                        import re
                        metric_patterns_found = re.findall(r'Metric \d+[:\*\#]*', analysis_text)
                        print(f"🔍 Debug - Available patterns in response: {metric_patterns_found}")
                    # Keep original values if pattern not found
                    enhanced_batch[metric_idx]['metric_name'] = metric['metric_name']
                    enhanced_batch[metric_idx]['category'] = metric['category']
                    enhanced_batch[metric_idx]['type'] = determine_type_from_category(metric['category'])
                    enhanced_batch[metric_idx]['area'] = determine_area_from_category(metric['category'])
                    enhanced_batch[metric_idx]['importance'] = "Medium"
                    enhanced_batch[metric_idx]['importance_reasoning'] = "Pattern not found in LLM response"
    
    except Exception as e:
        print(f"⚠️ Error in combined processing: {e}")
        # Keep original values if processing fails
    
    return enhanced_batch

def process_all_metrics_combined(metrics, company, year):
    """Process all metrics using combined batch processing for efficiency"""
    print(f"🚀 Processing {len(metrics)} metrics with combined batch processing...")
    
    # Process in larger batches for efficiency (increased from 3 to 8)
    batch_size = 8
    processed_metrics = []
    
    for i in range(0, len(metrics), batch_size):
        batch = metrics[i:i + batch_size]
        print(f"📊 Processing combined batch {i//batch_size + 1}/{(len(metrics) + batch_size - 1)//batch_size}")
        
        processed_batch = process_metrics_combined_batch(batch, company, year)
        processed_metrics.extend(processed_batch)
    
    print(f"✅ Combined processing completed for {len(processed_metrics)} metrics")
    return processed_metrics

def main():
    parser = argparse.ArgumentParser(description="Enhanced Convert Comprehensive ESG Analysis to Dashboard Format")
    parser.add_argument("input_file", help="Path to comprehensive ESG analysis JSON file")
    parser.add_argument("output_file", help="Path to output dashboard JSON file")
    parser.add_argument("--company", default="Amazon", help="Company name (default: Amazon)")
    parser.add_argument("--year", default="2020", help="Report year (default: 2020)")
    
    args = parser.parse_args()
    
    # Convert the comprehensive analysis to enhanced dashboard format
    result = convert_comprehensive_to_dashboard_enhanced(
        input_file=args.input_file,
        output_file=args.output_file,
        company=args.company,
        year=args.year
    )
    
    if result:
        print(f"\n✅ Conversion completed successfully!")
        print(f"📁 Output: {result}")
    else:
        print(f"\n❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 