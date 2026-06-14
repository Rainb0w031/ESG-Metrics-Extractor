#!/usr/bin/env python3
"""
Dynamic Comparison Analyzer for ESG Reports
Analyzes any pair of ESG reports using LLM and stores results to avoid redundant analysis.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import sys

# Add parent directory (metrics/) to path to import the modular API config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.api import APIConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicComparisonAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the analyzer with API configuration."""
        # Use the modular project's API config (.env -> DeepSeek by default)
        config = APIConfig.from_env()
        self.api_key = api_key or config.api_key
        self.api_url = config.api_base
        self.model = config.model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Create comparison storage directory
        self.comparison_dir = Path("comparison_analysis")
        self.comparison_dir.mkdir(exist_ok=True)
    
    def _make_api_request(self, messages, max_tokens=4000, temperature=0.1, timeout=120):
        """Make API request using direct requests with improved error handling."""
        import time
        
        # Retry configuration
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                logger.info(f"Making API request (attempt {attempt + 1}/{max_retries}) with timeout {timeout}s")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    logger.info(f"API request successful (attempt {attempt + 1})")
                    return content
                else:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    if response.status_code == 429:  # Rate limit
                        delay = base_delay * (2 ** attempt)
                        logger.info(f"Rate limited, waiting {delay}s before retry")
                        time.sleep(delay)
                        continue
                    elif response.status_code >= 500:  # Server error
                        delay = base_delay * (2 ** attempt)
                        logger.info(f"Server error, waiting {delay}s before retry")
                        time.sleep(delay)
                        continue
                    else:
                        # Client error, don't retry
                        return None
                        
            except requests.exceptions.Timeout:
                logger.warning(f"API request timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Waiting {delay}s before retry")
                    time.sleep(delay)
                    # Increase timeout for next attempt
                    timeout = min(timeout * 1.5, 300)  # Max 5 minutes
                else:
                    logger.error("All API request attempts timed out")
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Waiting {delay}s before retry")
                    time.sleep(delay)
                else:
                    logger.error("All API request attempts failed due to connection errors")
                    return None
                    
            except Exception as e:
                logger.error(f"Unexpected API request error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Waiting {delay}s before retry")
                    time.sleep(delay)
                else:
                    return None
        
        return None
    
    def _get_comparison_filename(self, company1: str, year1: str, company2: str, year2: str) -> str:
        """Generate filename for comparison analysis."""
        return f"{company1}_{year1}_vs_{company2}_{year2}_comparison.json"
    
    def _get_comparison_filepath(self, company1: str, year1: str, company2: str, year2: str) -> Path:
        """Get filepath for comparison analysis."""
        filename = self._get_comparison_filename(company1, year1, company2, year2)
        return self.comparison_dir / filename
    
    def comparison_exists(self, company1: str, year1: str, company2: str, year2: str) -> bool:
        """Check if comparison analysis already exists."""
        filepath = self._get_comparison_filepath(company1, year1, company2, year2)
        return filepath.exists()
    
    def load_existing_comparison(self, company1: str, year1: str, company2: str, year2: str) -> Optional[Dict[str, Any]]:
        """Load existing comparison analysis if it exists."""
        filepath = self._get_comparison_filepath(company1, year1, company2, year2)
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing comparison: {e}")
        return None
    
    def save_comparison_analysis(self, analysis: Dict[str, Any], company1: str, year1: str, company2: str, year2: str):
        """Save comparison analysis to file."""
        filepath = self._get_comparison_filepath(company1, year1, company2, year2)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved comparison analysis to {filepath}")
        except Exception as e:
            logger.error(f"Error saving comparison analysis: {e}")
    
    def analyze_metrics_comparison(self, metrics1: List[Dict], metrics2: List[Dict], 
                                 company1: str, year1: str, company2: str, year2: str) -> Dict[str, Any]:
        """Analyze metrics comparison using LLM with improved semantic understanding and chunking."""
        
        # Calculate input size and determine if chunking is needed
        metrics1_text = self._format_metrics_for_llm(metrics1, company1, year1)
        metrics2_text = self._format_metrics_for_llm(metrics2, company2, year2)
        
        # Estimate input size (rough calculation)
        input_size = len(metrics1_text) + len(metrics2_text)
        max_input_size = 25000  # Conservative limit to stay well under 30720
        
        if input_size > max_input_size:
            logger.info(f"Input size ({input_size}) exceeds limit ({max_input_size}), using chunked analysis")
            return self._analyze_metrics_chunked(metrics1, metrics2, company1, year1, company2, year2)
        else:
            logger.info(f"Input size ({input_size}) within limits, using direct analysis")
            return self._analyze_metrics_direct(metrics1, metrics2, company1, year1, company2, year2)
    
    def _analyze_metrics_direct(self, metrics1: List[Dict], metrics2: List[Dict], 
                              company1: str, year1: str, company2: str, year2: str) -> Dict[str, Any]:
        """Direct analysis for smaller metric sets."""
        
        # Prepare metrics for LLM analysis
        metrics1_text = self._format_metrics_for_llm(metrics1, company1, year1)
        metrics2_text = self._format_metrics_for_llm(metrics2, company2, year2)
        
        prompt = f"""
You are an expert ESG analyst performing precise metric matching between two companies' sustainability reports.

Report A: {company1} {year1} ESG Report
Report B: {company2} {year2} ESG Report

CRITICAL MATCHING RULES:
1. **Semantic Similarity Only**: Only match metrics that measure the SAME underlying concept
2. **Scope Awareness**: 
   - Scope 1 emissions ≠ Scope 2 emissions ≠ Scope 3 emissions
   - Direct emissions ≠ Indirect emissions
3. **Metric Type Distinction**:
   - Energy consumption ≠ Energy-related emissions
   - Renewable energy percentage ≠ Energy efficiency
   - Biodiversity impact ≠ Diversity & inclusion initiatives
   - Carbon intensity ≠ Total carbon emissions
4. **Unit Compatibility**: Only match metrics with compatible units
   - CO2e units can be compared (tons, Mt, MMT)
   - Energy units can be compared (MWh, kWh, GJ)
   - Percentage vs absolute values are NOT comparable
5. **Value Validation**: Avoid matching N/A values with actual values

Report A Metrics:
{metrics1_text}

Report B Metrics:
{metrics2_text}

Please provide a JSON response with the following structure:
{{
    "comparison_summary": {{
        "total_metrics_a": <number>,
        "total_metrics_b": <number>,
        "similar_metrics": <number>,
        "unique_to_a": <number>,
        "unique_to_b": <number>,
        "overall_comparability": "High/Medium/Low"
    }},
    "similar_metrics": [
        {{
            "metric_a": "<{company1} {year1} metric name>",
            "metric_b": "<{company2} {year2} metric name>",
            "value_a": "<value with unit from {company1} {year1}>",
            "value_b": "<value with unit from {company2} {year2}>",
            "category": "<ESG category>",
            "similarity_confidence": "High/Medium/Low",
            "analysis": "<objective comparison focusing on quantity differences>"
        }}
    ],
    "unique_metrics_a": [
        {{
            "metric": "<{company1} {year1} metric name>",
            "value": "<value with unit>",
            "category": "<ESG category>",
            "significance": "<why this metric is important for {company1} {year1}>"
        }}
    ],
    "unique_metrics_b": [
        {{
            "metric": "<{company2} {year2} metric name>",
            "value": "<value with unit>",
            "category": "<ESG category>",
            "significance": "<why this metric is important for {company2} {year2}>"
        }}
    ],
    "key_insights": [
        "<objective insight 1 about quantity differences between {company1} {year1} and {company2} {year2}>",
        "<objective insight 2 about reporting approaches>",
        "<objective insight 3 about ESG metric coverage differences>"
    ],
    "analysis_timestamp": "<current timestamp>"
}}

MATCHING EXAMPLES:
✅ CORRECT MATCHES:
- "Scope 1 Carbon Emissions" ↔ "Direct Operations Carbon Emissions"
- "Energy Consumption" ↔ "Total Energy Use"
- "Water Usage" ↔ "Water Consumption"
- "Waste Generated" ↔ "Total Waste"

❌ INCORRECT MATCHES:
- "Biodiversity Impact" ↔ "Diversity & Inclusion Initiatives"
- "Scope 1 Emissions" ↔ "Scope 2 Emissions"
- "Energy Efficiency" ↔ "Energy-Related Carbon Emissions"
- "Renewable Energy Percentage" ↔ "Carbon Emissions"

Use objective language: "higher", "lower", "more", "less", "greater", "smaller", "increased", "decreased".
Avoid subjective terms: "better", "worse", "superior", "inferior".

Respond only with valid JSON.
"""
        
        try:
            response = self._make_api_request([{"role": "user", "content": prompt}])
            if response:
                # Clean and parse JSON response
                if response.startswith('```json'):
                    response = response[7:]
                if response.endswith('```'):
                    response = response[:-3]
                
                analysis = json.loads(response.strip())
                analysis['analysis_timestamp'] = datetime.now().isoformat()
                analysis['companies'] = {
                    'company_a': {'name': company1, 'year': year1},
                    'company_b': {'name': company2, 'year': year2}
                }
                return analysis
            else:
                logger.error("Failed to get LLM response")
                return self._generate_fallback_analysis(metrics1, metrics2, company1, year1, company2, year2)
                
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return self._generate_fallback_analysis(metrics1, metrics2, company1, year1, company2, year2)
    
    def _analyze_metrics_chunked(self, metrics1: List[Dict], metrics2: List[Dict], 
                               company1: str, year1: str, company2: str, year2: str) -> Dict[str, Any]:
        """Chunked analysis for large metric sets with optimized chunk sizes."""
        
        logger.info(f"Starting chunked analysis for {len(metrics1)} + {len(metrics2)} metrics")
        
        # Use smaller chunk sizes to reduce timeout risk
        total_metrics = len(metrics1) + len(metrics2)
        if total_metrics <= 100:
            chunk_size = 30
        elif total_metrics <= 300:
            chunk_size = 50
        elif total_metrics <= 600:
            chunk_size = 80
        else:
            chunk_size = 100  # Reduced from 150 to 100
        
        logger.info(f"Using chunk size: {chunk_size}")
        
        # Split metrics into chunks
        chunks1 = [metrics1[i:i + chunk_size] for i in range(0, len(metrics1), chunk_size)]
        chunks2 = [metrics2[i:i + chunk_size] for i in range(0, len(metrics2), chunk_size)]
        
        logger.info(f"Split into {len(chunks1)} chunks for {company1} and {len(chunks2)} chunks for {company2}")
        
        # Analyze each chunk pair
        all_similar_metrics = []
        all_unique_a = []
        all_unique_b = []
        
        # Track which metrics from company B have been matched
        matched_metrics_b = set()
        
        # Track failed chunk pairs for fallback
        failed_chunks = []
        
        for i, chunk1 in enumerate(chunks1):
            logger.info(f"Processing chunk {i+1}/{len(chunks1)} for {company1}")
            
            for j, chunk2 in enumerate(chunks2):
                logger.info(f"  Comparing with chunk {j+1}/{len(chunks2)} for {company2}")
                
                try:
                    # Analyze this chunk pair
                    chunk_analysis = self._analyze_metrics_direct(chunk1, chunk2, company1, year1, company2, year2)
                    
                    # Collect similar metrics
                    similar_metrics = chunk_analysis.get('similar_metrics', [])
                    for pair in similar_metrics:
                        metric_b_name = pair.get('metric_b', '')
                        if metric_b_name not in matched_metrics_b:
                            all_similar_metrics.append(pair)
                            matched_metrics_b.add(metric_b_name)
                    
                    # Collect unique metrics from company A (only if not matched in any chunk)
                    if j == 0:  # Only add unique metrics from company A in first iteration
                        unique_a = chunk_analysis.get('unique_metrics_a', [])
                        for metric in unique_a:
                            metric_name = metric.get('metric', '')
                            # Check if this metric was matched in any chunk
                            if not any(metric_name == pair.get('metric_a', '') for pair in all_similar_metrics):
                                all_unique_a.append(metric)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze chunk pair {i+1}-{j+1}: {e}")
                    failed_chunks.append((i, j, chunk1, chunk2))
                    # Continue with other chunks
                    continue
            
            # Add remaining unique metrics from company A that weren't matched
            for metric in chunk1:
                metric_name = f"{company1} {year1} - {metric.get('metric_name', '')}"
                if not any(metric_name == pair.get('metric_a', '') for pair in all_similar_metrics):
                    all_unique_a.append({
                        'metric': metric_name,
                        'value': f"{metric.get('value', '')} {metric.get('unit', '')}".strip(),
                        'category': metric.get('category', ''),
                        'significance': f'Unique to {company1} {year1} ESG Report'
                    })
        
        # Process failed chunks using fallback analysis
        if failed_chunks:
            logger.info(f"Processing {len(failed_chunks)} failed chunk pairs using fallback analysis")
            for i, j, chunk1, chunk2 in failed_chunks:
                try:
                    fallback_analysis = self._generate_fallback_analysis(chunk1, chunk2, company1, year1, company2, year2)
                    similar_metrics = fallback_analysis.get('similar_metrics', [])
                    for pair in similar_metrics:
                        metric_b_name = pair.get('metric_b', '')
                        if metric_b_name not in matched_metrics_b:
                            all_similar_metrics.append(pair)
                            matched_metrics_b.add(metric_b_name)
                except Exception as e:
                    logger.error(f"Fallback analysis also failed for chunk pair {i+1}-{j+1}: {e}")
        
        # Collect unique metrics from company B (not matched in any chunk)
        for chunk2 in chunks2:
            for metric in chunk2:
                metric_name = f"{company2} {year2} - {metric.get('metric_name', '')}"
                if metric_name not in matched_metrics_b:
                    all_unique_b.append({
                        'metric': metric_name,
                        'value': f"{metric.get('value', '')} {metric.get('unit', '')}".strip(),
                        'category': metric.get('category', ''),
                        'significance': f'Unique to {company2} {year2} ESG Report'
                    })
        
        # Generate insights based on chunked analysis
        key_insights = [
            f"{company1} {year1} ESG Report contains {len(metrics1)} metrics",
            f"{company2} {year2} ESG Report contains {len(metrics2)} metrics",
            f"Found {len(all_similar_metrics)} semantically similar metrics between {company1} {year1} and {company2} {year2}",
            f"Analysis performed using chunked approach with {len(chunks1)} x {len(chunks2)} chunk pairs"
        ]
        
        if failed_chunks:
            key_insights.append(f"Note: {len(failed_chunks)} chunk pairs used fallback analysis due to API timeouts")
        
        # Determine overall comparability
        if len(all_similar_metrics) > 20:
            overall_comparability = "High"
        elif len(all_similar_metrics) > 10:
            overall_comparability = "Medium"
        else:
            overall_comparability = "Low"
        
        logger.info(f"Chunked analysis completed: {len(all_similar_metrics)} similar metrics found")
        
        return {
            'comparison_summary': {
                'total_metrics_a': len(metrics1),
                'total_metrics_b': len(metrics2),
                'similar_metrics': len(all_similar_metrics),
                'unique_to_a': len(all_unique_a),
                'unique_to_b': len(all_unique_b),
                'overall_comparability': overall_comparability
            },
            'similar_metrics': all_similar_metrics,
            'unique_metrics_a': all_unique_a,
            'unique_metrics_b': all_unique_b,
            'key_insights': key_insights,
            'analysis_timestamp': datetime.now().isoformat(),
            'companies': {
                'company_a': {'name': company1, 'year': year1},
                'company_b': {'name': company2, 'year': year2}
            },
            'analysis_method': 'chunked',
            'failed_chunks': len(failed_chunks)
        }
    
    def _format_metrics_for_llm(self, metrics: List[Dict], company: str, year: str) -> str:
        """Format metrics for LLM analysis."""
        formatted_metrics = []
        
        for metric in metrics:
            metric_info = {
                'name': f"{company} {year} - {metric.get('metric_name', 'Unknown')}",
                'value': f"{metric.get('value', 'N/A')} {metric.get('unit', '')}".strip(),
                'category': metric.get('category', 'Unknown'),
                'area': metric.get('area', 'Unknown'),
                'unit': metric.get('unit', ''),
                'description': metric.get('description', ''),
                'raw_value': metric.get('value', 'N/A'),
                'raw_unit': metric.get('unit', '')
            }
            formatted_metrics.append(metric_info)
        
        return json.dumps(formatted_metrics, indent=2, ensure_ascii=False)
    
    def _generate_fallback_analysis(self, metrics1: List[Dict], metrics2: List[Dict], 
                                  company1: str, year1: str, company2: str, year2: str) -> Dict[str, Any]:
        """Generate improved fallback analysis with semantic understanding."""
        logger.info("Generating improved fallback analysis")
        
        similar_metrics = []
        unique_a = []
        unique_b = []
        
        # Define semantic matching patterns
        semantic_patterns = {
            'scope_1_emissions': [
                ['scope 1', 'direct', 'direct operations', 'direct emissions'],
                ['carbon', 'co2', 'co2e', 'emissions', 'greenhouse gas']
            ],
            'scope_2_emissions': [
                ['scope 2', 'indirect', 'purchased electricity', 'energy-related'],
                ['carbon', 'co2', 'co2e', 'emissions', 'greenhouse gas']
            ],
            'scope_3_emissions': [
                ['scope 3', 'value chain', 'supply chain', 'indirect emissions'],
                ['carbon', 'co2', 'co2e', 'emissions', 'greenhouse gas']
            ],
            'energy_consumption': [
                ['energy', 'electricity', 'power'],
                ['consumption', 'use', 'usage', 'demand', 'total']
            ],
            'water_usage': [
                ['water'],
                ['consumption', 'use', 'usage', 'withdrawal']
            ],
            'waste_generation': [
                ['waste'],
                ['generated', 'produced', 'disposal', 'management', 'total']
            ],
            'renewable_energy': [
                ['renewable', 'clean energy', 'solar', 'wind'],
                ['energy', 'electricity', 'power', 'percentage', 'usage']
            ],
            'diversity_inclusion': [
                ['diversity', 'inclusion', 'workforce', 'employee'],
                ['representation', 'percentage', 'initiatives', 'programs']
            ]
        }
        
        def semantic_similarity(metric1_name, metric2_name):
            """Check semantic similarity using defined patterns."""
            metric1_lower = metric1_name.lower()
            metric2_lower = metric2_name.lower()
            
            # Check for exact scope mismatches
            if ('scope 1' in metric1_lower and 'scope 2' in metric2_lower) or \
               ('scope 1' in metric2_lower and 'scope 2' in metric1_lower):
                return False, 0
            
            if ('scope 1' in metric1_lower and 'scope 3' in metric2_lower) or \
               ('scope 1' in metric2_lower and 'scope 3' in metric1_lower):
                return False, 0
            
            if ('scope 2' in metric1_lower and 'scope 3' in metric2_lower) or \
               ('scope 2' in metric2_lower and 'scope 3' in metric1_lower):
                return False, 0
            
            # Check for metric type mismatches
            if ('biodiversity' in metric1_lower and 'diversity' in metric2_lower and 'inclusion' in metric2_lower) or \
               ('biodiversity' in metric2_lower and 'diversity' in metric1_lower and 'inclusion' in metric1_lower):
                return False, 0
            
            if ('energy' in metric1_lower and 'emission' in metric2_lower) or \
               ('energy' in metric2_lower and 'emission' in metric1_lower):
                return False, 0
            
            if ('renewable' in metric1_lower and 'emission' in metric2_lower) or \
               ('renewable' in metric2_lower and 'emission' in metric1_lower):
                return False, 0
            
            # Special case: Direct Operations Carbon Emissions should match Scope 1
            if (('scope 1' in metric1_lower and 'direct operations' in metric2_lower) or \
                ('scope 1' in metric2_lower and 'direct operations' in metric1_lower)) and \
               ('carbon' in metric1_lower and 'carbon' in metric2_lower):
                return True, 0.9
            
            # Check semantic patterns
            for pattern_name, pattern_groups in semantic_patterns.items():
                group1_match = any(all(term in metric1_lower for term in group) for group in pattern_groups)
                group2_match = any(all(term in metric2_lower for term in group) for group in pattern_groups)
                
                if group1_match and group2_match:
                    # Calculate confidence based on pattern match
                    confidence = 0.8 if pattern_name in ['scope_1_emissions', 'scope_2_emissions', 'scope_3_emissions'] else 0.6
                    return True, confidence
            
            return False, 0
        
        def unit_compatibility(unit1, unit2):
            """Check if units are compatible for comparison."""
            if not unit1 or not unit2:
                return False
            
            unit1_lower = unit1.lower()
            unit2_lower = unit2.lower()
            
            # CO2e units
            co2e_units = ['co2e', 'co₂e', 'tons co2e', 'mt co2e', 'mmt co2e', 'kg co2e']
            if any(u in unit1_lower for u in co2e_units) and any(u in unit2_lower for u in co2e_units):
                return True
            
            # Energy units
            energy_units = ['mwh', 'kwh', 'gj', 'btu', 'j']
            if any(u in unit1_lower for u in energy_units) and any(u in unit2_lower for u in energy_units):
                return True
            
            # Water units
            water_units = ['m3', 'liters', 'gallons', 'cubic meters']
            if any(u in unit1_lower for u in water_units) and any(u in unit2_lower for u in water_units):
                return True
            
            # Waste units
            waste_units = ['tons', 'kg', 'pounds', 'metric tons']
            if any(u in unit1_lower for u in waste_units) and any(u in unit2_lower for u in waste_units):
                return True
            
            # Percentage units
            if ('%' in unit1_lower or 'percent' in unit1_lower) and ('%' in unit2_lower or 'percent' in unit2_lower):
                return True
            
            return False
        
        # Find similar metrics using improved logic
        for metric1 in metrics1:
            metric1_name = metric1.get('metric_name', '')
            metric1_value = metric1.get('value', '')
            metric1_unit = metric1.get('unit', '')
            
            # Skip N/A values
            if metric1_value == 'N/A':
                unique_a.append({
                    'metric': f"{company1} {year1} - {metric1_name}",
                    'value': f"{metric1_value} {metric1_unit}".strip(),
                    'category': metric1.get('category', ''),
                    'significance': f'Unique to {company1} {year1} ESG Report (N/A value)'
                })
                continue
            
            best_match = None
            best_confidence = 0
            
            for metric2 in metrics2:
                metric2_name = metric2.get('metric_name', '')
                metric2_value = metric2.get('value', '')
                metric2_unit = metric2.get('unit', '')
                
                # Skip N/A values
                if metric2_value == 'N/A':
                    continue
                
                # Check semantic similarity
                is_similar, confidence = semantic_similarity(metric1_name, metric2_name)
                
                if is_similar and confidence > best_confidence:
                    # Check unit compatibility
                    if unit_compatibility(metric1_unit, metric2_unit):
                        best_match = metric2
                        best_confidence = confidence
            
            if best_match and best_confidence >= 0.6:
                similar_metrics.append({
                    'metric_a': f"{company1} {year1} - {metric1_name}",
                    'metric_b': f"{company2} {year2} - {best_match.get('metric_name', '')}",
                    'value_a': f"{metric1_value} {metric1_unit}".strip(),
                    'value_b': f"{best_match.get('value', '')} {best_match.get('unit', '')}".strip(),
                    'category': metric1.get('category', ''),
                    'similarity_confidence': 'High' if best_confidence >= 0.8 else 'Medium',
                    'analysis': f'Semantic similarity match between {company1} {year1} ({metric1_value} {metric1_unit}) and {company2} {year2} ({best_match.get("value", "")} {best_match.get("unit", "")})'
                })
            else:
                unique_a.append({
                    'metric': f"{company1} {year1} - {metric1_name}",
                    'value': f"{metric1_value} {metric1_unit}".strip(),
                    'category': metric1.get('category', ''),
                    'significance': f'Unique to {company1} {year1} ESG Report'
                })
        
        # Find unique metrics for company B (not matched above)
        matched_metrics_b = {pair['metric_b'] for pair in similar_metrics}
        for metric2 in metrics2:
            metric2_name = metric2.get('metric_name', '')
            metric2_value = metric2.get('value', '')
            metric2_unit = metric2.get('unit', '')
            
            metric_b_full_name = f"{company2} {year2} - {metric2_name}"
            if metric_b_full_name not in matched_metrics_b:
                unique_b.append({
                    'metric': metric_b_full_name,
                    'value': f"{metric2_value} {metric2_unit}".strip(),
                    'category': metric2.get('category', ''),
                    'significance': f'Unique to {company2} {year2} ESG Report'
                })
        
        return {
            'comparison_summary': {
                'total_metrics_a': len(metrics1),
                'total_metrics_b': len(metrics2),
                'similar_metrics': len(similar_metrics),
                'unique_to_a': len(unique_a),
                'unique_to_b': len(unique_b),
                'overall_comparability': 'High' if len(similar_metrics) > 10 else 'Medium' if len(similar_metrics) > 5 else 'Low'
            },
            'similar_metrics': similar_metrics,
            'unique_metrics_a': unique_a,
            'unique_metrics_b': unique_b,
            'key_insights': [
                f"{company1} {year1} ESG Report contains {len(metrics1)} metrics",
                f"{company2} {year2} ESG Report contains {len(metrics2)} metrics",
                f"Found {len(similar_metrics)} semantically similar metrics between {company1} {year1} and {company2} {year2}"
            ],
            'analysis_timestamp': datetime.now().isoformat(),
            'companies': {
                'company_a': {'name': company1, 'year': year1},
                'company_b': {'name': company2, 'year': year2}
            }
        }
    
    def analyze_pair(self, metrics1: List[Dict], metrics2: List[Dict], 
                    company1: str, year1: str, company2: str, year2: str) -> Dict[str, Any]:
        """Analyze a pair of reports, using cached results if available."""
        
        # Check if analysis already exists
        if self.comparison_exists(company1, year1, company2, year2):
            logger.info(f"Loading existing comparison: {company1} {year1} vs {company2} {year2}")
            return self.load_existing_comparison(company1, year1, company2, year2)
        
        # Perform new analysis
        logger.info(f"Performing new comparison analysis: {company1} {year1} vs {company2} {year2}")
        analysis = self.analyze_metrics_comparison(metrics1, metrics2, company1, year1, company2, year2)
        
        # Save analysis for future use
        self.save_comparison_analysis(analysis, company1, year1, company2, year2)
        
        return analysis

# Global analyzer instance
comparison_analyzer = DynamicComparisonAnalyzer() 