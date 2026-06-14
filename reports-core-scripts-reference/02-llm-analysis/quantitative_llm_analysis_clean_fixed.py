#!/usr/bin/env python3
"""
Clean Quantitative LLM Analysis for ESG Reports
Removes all mock data fallbacks and only uses actual LLM analysis
"""

import json
import re
from pathlib import Path
import sys
import argparse
import os

# Ensure the llm module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from direct_api_client import make_direct_api_call

# Config
parser = argparse.ArgumentParser(description="LLM quantitative analysis for ESG reports.")
parser.add_argument("input_json", help="Path to the structured content JSON.")
parser.add_argument("output_json", help="Path to save the quant summary JSON.")
args = parser.parse_args()
INPUT_JSON = args.input_json
OUTPUT_JSON = args.output_json

# Load extracted segments
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract ALL text content from the structured JSON
all_text_content = []

for page in data.get("pages", []):
    # Add text from structured segments
    for segment in page.get("text_segments", []):
        text = segment.get("text", "")
        if text and len(text.strip()) > 10:  # Only add substantial text
            all_text_content.append(text)
    
    # Add original text if it exists and is substantial
    original_text = page.get("original_text", "")
    if original_text and len(original_text.strip()) > 50:  # Only add substantial text
        all_text_content.append(original_text)

if not all_text_content:
    print(f"No text content found in {INPUT_JSON}!")
    exit(1)

print(f"Found {len(all_text_content)} text segments for comprehensive Environmental, Social and Governance analysis")

# Chunking configuration for API processing
CHUNK_SIZE = 40  # Increased from 30 for better efficiency while staying within API limits
MAX_CHUNKS_PER_ANALYSIS = None  # No limit - process all chunks
TOTAL_MAX_CHUNKS = None  # No limit - process all chunks

def chunk_text_content(text_segments, chunk_size=CHUNK_SIZE):
    """Split text segments into manageable chunks"""
    chunks = []
    for i in range(0, len(text_segments), chunk_size):
        chunk = text_segments[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def process_chunks_with_llm(text_chunks, prompt_template, analysis_type, max_chunks=None):
    """Process text chunks with LLM and combine results"""
    print(f"PROCESSING: Processing {analysis_type} data with ALL {len(text_chunks)} chunks...")
    
    # Process ALL chunks - no limits
    combined_results = {}
    
    for i, chunk in enumerate(text_chunks):
        print(f"PROCESSING: {analysis_type} chunk {i+1}/{len(text_chunks)} ({len(chunk)} segments)")
        
        # Create prompt for this chunk
        chunk_text = chr(10).join(chunk)
        chunk_prompt = prompt_template.replace(
            f"TEXT TO ANALYZE:\n{chr(10).join(all_text_content)}\n",
            f"TEXT TO ANALYZE (CHUNK {i+1}/{len(text_chunks)}):\n{chunk_text}\n"
        )
        
        # Add chunk-specific instructions
        chunk_prompt += f"\n\nIMPORTANT: This is chunk {i+1} of {len(text_chunks)}. Focus on extracting metrics from this specific text segment."
        
        messages = [
            {"role": "system", "content": f"You are an expert ESG analyst that only responds with comprehensive, detailed JSON categorizations of {analysis_type.lower()} data."},
            {"role": "user", "content": chunk_prompt}
        ]
        
        try:
            response = make_direct_api_call(messages, temperature=0.2, max_tokens=4096, timeout=120, max_retries=3)
            if response is None:
                print(f"WARNING: API failed for {analysis_type} chunk {i+1} - skipping")
                continue
                
            response_text = extract_response_text(response)
            if response_text is None:
                print(f"WARNING: Failed to extract {analysis_type} chunk {i+1} response - skipping")
                continue
                
            try:
                chunk_result = json.loads(response_text)
                # Merge results (simple merge for now)
                combined_results = merge_esg_results(combined_results, chunk_result, analysis_type)
                print(f"SUCCESS: Processed {analysis_type} chunk {i+1}")
                
            except json.JSONDecodeError as e:
                print(f"WARNING: Failed to parse {analysis_type} chunk {i+1} JSON: {e} - skipping")
                continue
                
        except Exception as e:
            print(f"WARNING: Failed to process {analysis_type} chunk {i+1}: {e} - skipping")
            continue
    
    return combined_results

def merge_esg_results(existing_results, new_results, analysis_type):
    """Merge ESG analysis results from multiple chunks"""
    if not existing_results:
        return new_results
    
    # Get the main analysis key
    if analysis_type == "Environmental":
        main_key = "environmental_comprehensive"
    elif analysis_type == "Social":
        main_key = "social_comprehensive"
    elif analysis_type == "Governance":
        main_key = "governance_comprehensive"
    else:
        return existing_results
    
    # If existing_results doesn't have the main key but new_results does, use new_results as base
    if main_key not in existing_results and main_key in new_results:
        return new_results
    
    # If neither has the main key, return new_results (might be empty or have different structure)
    if main_key not in existing_results and main_key not in new_results:
        return new_results
    
    # If existing_results has the main key but new_results doesn't, keep existing
    if main_key in existing_results and main_key not in new_results:
        return existing_results
    
    # Both have the main key, proceed with merging
    existing_main = existing_results[main_key]
    new_main = new_results[main_key]
    
    # Merge each category
    for category in new_main:
        if category in existing_main:
            existing_category = existing_main[category]
            new_category = new_main[category]
            
            # Merge details and metrics
            if isinstance(existing_category, dict) and isinstance(new_category, dict):
                for subcategory in new_category:
                    if subcategory in existing_category:
                        existing_sub = existing_category[subcategory]
                        new_sub = new_category[subcategory]
                        
                        # Merge details (lists)
                        if "details" in existing_sub and "details" in new_sub:
                            existing_sub["details"].extend(new_sub["details"])
                        
                        # Merge metrics (dicts)
                        if "metrics" in existing_sub and "metrics" in new_sub:
                            existing_sub["metrics"].update(new_sub["metrics"])
                        
                        # Merge lists
                        elif isinstance(existing_sub, list) and isinstance(new_sub, list):
                            existing_sub.extend(new_sub)
                    else:
                        existing_category[subcategory] = new_category[subcategory]
            else:
                # Handle direct lists
                if isinstance(existing_category, list) and isinstance(new_category, list):
                    existing_category.extend(new_category)
        else:
            # Add new category
            existing_main[category] = new_main[category]
    
    return existing_results

# Create text chunks for processing
text_chunks = chunk_text_content(all_text_content, CHUNK_SIZE)
print(f"Created {len(text_chunks)} chunks of {CHUNK_SIZE} segments each")

# Process ALL chunks - no limits
print(f"PRODUCTION MODE: Processing ALL {len(text_chunks)} chunks with {CHUNK_SIZE} segments each")

# Extract year from input file path for dynamic prompts
input_path = Path(INPUT_JSON)
year_match = re.search(r'(\d{4})', input_path.name)
year = year_match.group(1) if year_match else "2021"  # Default to 2021 if not found

print(f"Processing data for year: {year}")

# Load existing Environmental data (if available)
existing_env_file = f"json/Amazon/{year}/amazon_{year}_quant_summary.json"
existing_env_data = {}
if os.path.exists(existing_env_file):
    try:
        with open(existing_env_file, "r", encoding="utf-8") as f:
            existing_env_data = json.load(f)
        print(f"SUCCESS: Loaded existing Environmental data from {existing_env_file}")
    except Exception as e:
        print(f"WARNING: Could not load existing Environmental data: {e}")
else:
    print(f"Warning: Existing Environmental file not found: {existing_env_file}")

# FIXED Comprehensive LLM prompt for detailed Environmental (E) analysis
environmental_prompt = (
    f"You are an expert ESG analyst specializing in Environmental (E) data extraction and categorization. "
    f"Analyze the following text content from the {year} Sustainability Report and extract ALL environmental information. "
    f"Provide a comprehensive, detailed categorization of environmental data including both quantitative metrics and qualitative information. "
    
    "CRITICAL REQUIREMENTS:\n"
    "1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS from the text\n"
    "2. Populate 'metrics' objects with actual numerical values (e.g., 'emissions_2021': '51.17 MMT CO2e')\n"
    "3. Include both quantitative data (numbers, percentages, metrics) and qualitative information (goals, strategies, initiatives)\n"
    "4. Preserve exact numbers and units as mentioned in the text\n"
    "5. Your response MUST be a single, valid JSON object and nothing else\n"
    "6. If you find numbers in the text, ALWAYS put them in the 'metrics' section\n"
    "7. AVOID REDUNDANT METRIC NAMES - use only ONE metric name per value\n"
    "8. For emissions, prioritize NET emissions over gross emissions when both are mentioned\n"
    "9. Use consistent metric naming: prefer 'scope_1_net_emissions_2024' over 'scope_1_emissions'\n"
    "10. CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly as mentioned in text\n"
    "11. CRITICAL: DO NOT SUMMARIZE OR MODIFY ORIGINAL TEXT in details\n"
    "12. CRITICAL: Details should contain ORIGINAL TEXT SEGMENTS exactly as they appear\n"
    "13. CRITICAL: Only replace underscores with spaces in structured JSON, nothing else\n"
    "14. CRITICAL: If text says '717,000 tons', use '717,000 tons' - do not convert to MtCO2e\n"
    "15. CRITICAL: If text says '3.732 million tons', use '3.732 million tons' - do not convert\n"
    "16. CRITICAL: If text says '1.5 gigatons', use '1.5 gigatons' - do not convert to tons\n"
    "17. CRITICAL: If text says '33.338 million tons', use '33.338 million tons' - do not convert\n"
    
    "SCOPE 3+ CONCEPT UNDERSTANDING:\n"
    "- Scope 3+ is a unique concept introduced by Alibaba that goes beyond traditional Scope 3 emissions\n"
    "- Scope 3+ includes 'enabled and engaged' emissions reductions through platform ecosystem\n"
    "- When text mentions 'platform ecosystem', 'enabled and engaged', or 'Scope 3+', categorize as scope_3_plus\n"
    "- Traditional Scope 3 refers to value chain emissions (upstream/downstream)\n"
    "- Scope 3+ refers to broader ecosystem-driven reductions beyond the value chain\n"
    "- CRITICAL: Distinguish between traditional Scope 3 and Scope 3+ concepts\n"
    
    "EMISSIONS METRIC NAMING RULES:\n"
    "- Use 'scope_1_net_emissions_2024' for net Scope 1 emissions (not 'scope_1_emissions' or 'emissions_scope_1')\n"
    "- Use 'scope_2_net_emissions_2024' for net Scope 2 emissions (not 'scope_2_emissions' or 'emissions_scope_2')\n"
    "- Use 'scope_3_net_emissions_2024' for traditional net Scope 3 emissions (value chain only)\n"
    "- Use 'scope_3_plus_emissions_reduction_2024' for Scope 3+ emissions reductions (platform ecosystem)\n"
    "- Use 'scope_3_plus_cumulative_reduction_goal_2035' for Scope 3+ cumulative goals\n"
    "- Use 'total_net_emissions_2024' for total net emissions (Scopes 1+2)\n"
    "- Include year suffix for all emissions metrics (e.g., '_2024')\n"
    "- DO NOT create duplicate metrics with different names for the same value\n"
    "- If text mentions 'net emissions', use that value and specify 'net' in metric name\n"
    "- If text mentions 'gross emissions', use that value and specify 'gross' in metric name\n"
    "- CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly as mentioned in text\n"
    "- If text says '717,000 tons', use '717,000 tons' in metrics - do not convert to MtCO2e\n"
    "- If text says '3.732 million tons', use '3.732 million tons' in metrics - do not convert\n"
    "- If text says '1.5 gigatons', use '1.5 gigatons' in metrics - do not convert to tons\n"
    "- If text says '33.338 million tons', use '33.338 million tons' in metrics - do not convert\n"
    "- If text says '8.1 tons per million RMB', use '8.1 tons per million RMB' - do not convert\n"
    
    "UNIT PRESERVATION RULES:\n"
    "- CRITICAL: Preserve ALL unit prefixes exactly as mentioned in text\n"
    "- If text says 'gigatons', use 'gigatons' (not 'tons')\n"
    "- If text says 'million tons', use 'million tons' (not 'tons')\n"
    "- If text says 'billion tons', use 'billion tons' (not 'tons')\n"
    "- If text says 'thousand tons', use 'thousand tons' (not 'tons')\n"
    "- If text says 'MtCO2e', use 'MtCO2e' (not 'MMt CO2e')\n"
    "- If text says 'tCO2e', use 'tCO2e' (not 'tons')\n"
    "- DO NOT add or remove prefixes, multipliers, or unit conversions\n"
    
    "COMPOUND UNIT PRESERVATION - CRITICAL:\n"
    "- HIGHLIGHT: Compound units are complex units that combine multiple measurements\n"
    "- HIGHLIGHT: Carbon intensity metrics often use compound units\n"
    "- HIGHLIGHT: Preserve compound units EXACTLY as written - do not simplify or convert\n"
    "- Examples of compound units to preserve exactly:\n"
    "  * 'tons per million RMB' → keep as 'tons per million RMB' (do not convert to 'tons')\n"
    "  * 'grams CO2e per $ of sales' → keep as 'grams CO2e per $ of sales'\n"
    "  * 'tons per million dollars' → keep as 'tons per million dollars'\n"
    "  * 'kg CO2e per unit' → keep as 'kg CO2e per unit'\n"
    "  * 'tons per employee' → keep as 'tons per employee'\n"
    "  * 'MtCO2e per million RMB' → keep as 'MtCO2e per million RMB'\n"
    "- CRITICAL: Compound units represent intensity ratios and cannot be simplified\n"
    "- CRITICAL: Changing compound units changes the meaning of the metric\n"
    "- CRITICAL: If text says '8.1 tons per million RMB', use exactly that - do not convert to '8.1 tons'\n"
    
    "DETAILS REQUIREMENTS:\n"
    "- CRITICAL: Details should contain ORIGINAL TEXT SEGMENTS exactly as they appear in the source text\n"
    "- CRITICAL: DO NOT summarize, modify, or rephrase the original text\n"
    "- CRITICAL: DO NOT combine multiple text segments into one\n"
    "- CRITICAL: Only replace underscores with spaces in structured JSON format\n"
    "- CRITICAL: Preserve exact wording, punctuation, and structure of original text\n"
    "- CRITICAL: If original text says 'GHG emissions from our purchased electricity and heat (Scope 2) totaled 3.732 million tons', use exactly that text\n"
    "- CRITICAL: Do not add explanations, summaries, or modifications to the original text\n"
    
    "EXAMPLE METRICS FORMAT:\n"
    '  "metrics": {\n'
    '    "scope_1_net_emissions_2024": "717,096 tons",\n'
    '    "scope_2_net_emissions_2024": "3,732,075 tons",\n'
    '    "scope_3_net_emissions_intensity_2024": "8.1 tons per million RMB",\n'
    '    "scope_3_plus_emissions_reduction_2024": "33.338 million tons",\n'
    '    "scope_3_plus_cumulative_reduction_goal_2035": "1.5 gigatons",\n'
    '    "total_net_emissions_2024": "4,449,171 tons",\n'
    '    "renewable_energy_percentage": "85%",\n'
    '    "carbon_intensity_per_revenue": "122.8 grams CO2e per $ of sales",\n'
    '    "emissions_per_employee": "2.5 tons per employee",\n'
    '    "carbon_intensity_per_unit": "0.8 kg CO2e per unit"\n'
    '  }\n'
    '  "details": [\n'
    '    "Scope 1 net emissions totaled 717,096 tons in 2024, down from 928,939 tons in 2023",\n'
    '    "Scope 2 net emissions totaled 3,732,075 tons in 2024, down from 3,756,085 tons in 2023",\n'
    '    "Enabled and engaged the platform ecosystem to achieve 33.338 million tons of emissions reduction",\n'
    '    "Between 2021 and 2035, we will enable and engage the platform ecosystem to cumulatively reduce 1.5 gigatons of emissions"\n'
    '  ]\n'
    
    "CATEGORIZE INTO THESE DETAILED SECTIONS:\n"
    "{\n"
    '  "environmental_comprehensive": {\n'
    '    "emissions": {\n'
    '      "scope_1": {"details": [], "metrics": {}},\n'
    '      "scope_2": {"details": [], "metrics": {}},\n'
    '      "scope_3": {"details": [], "metrics": {}},\n'
    '      "scope_3_plus": {"details": [], "metrics": {}},\n'
    '      "total_emissions": {"details": [], "metrics": {}},\n'
    '      "carbon_intensity": {"details": [], "metrics": {}},\n'
    '      "emissions_reduction_goals": {"details": [], "metrics": {}},\n'
    '      "emissions_reduction_strategies": []\n'
    '    },\n'
    '    "energy": {\n'
    '      "renewable_energy": {"details": [], "metrics": {}},\n'
    '      "energy_efficiency": {"details": [], "metrics": {}},\n'
    '      "energy_consumption": {"details": [], "metrics": {}},\n'
    '      "carbon_free_energy": {"details": [], "metrics": {}},\n'
    '      "energy_projects": {"details": [], "metrics": {}},\n'
    '      "energy_goals": []\n'
    '    },\n'
    '    "water": {\n'
    '      "water_use": {"details": [], "metrics": {}},\n'
    '      "water_replenishment": {"details": [], "metrics": {}},\n'
    '      "water_intensity": {"details": [], "metrics": {}},\n'
    '      "water_positive_goals": {"details": [], "metrics": {}},\n'
    '      "water_conservation": []\n'
    '    },\n'
    '    "waste": {\n'
    '      "waste_generation": {"details": [], "metrics": {}},\n'
    '      "waste_reduction": {"details": [], "metrics": {}},\n'
    '      "recycling": {"details": [], "metrics": {}},\n'
    '      "circularity": {"details": [], "metrics": {}},\n'
    '      "packaging": {"details": [], "metrics": {}},\n'
    '      "food_waste": {"details": [], "metrics": {}}\n'
    '    },\n'
    '    "transportation": {\n'
    '      "electric_vehicles": {"details": [], "metrics": {}},\n'
    '      "delivery_optimization": {"details": [], "metrics": {}},\n'
    '      "transportation_emissions": {"details": [], "metrics": {}},\n'
    '      "logistics_efficiency": {"details": [], "metrics": {}},\n'
    '      "alternative_fuels": []\n'
    '    },\n'
    '    "buildings": {\n'
    '      "building_efficiency": {"details": [], "metrics": {}},\n'
    '      "embodied_carbon": {"details": [], "metrics": {}},\n'
    '      "construction_materials": {"details": [], "metrics": {}},\n'
    '      "building_certifications": []\n'
    '    },\n'
    '    "supply_chain": {\n'
    '      "supplier_engagement": [],\n'
    '      "supply_chain_emissions": {"details": [], "metrics": {}},\n'
    '      "supplier_decarbonization": []\n'
    '    },\n'
    '    "climate_pledge": {\n'
    '      "pledge_details": [],\n'
    '      "signatories": {"details": [], "metrics": {}},\n'
    '      "climate_fund": {"details": [], "metrics": {}},\n'
    '      "carbon_neutralization": []\n'
    '    },\n'
    '    "biodiversity": {\n'
    '      "deforestation": [],\n'
    '      "forest_conservation": [],\n'
    '      "nature_based_solutions": []\n'
    '    },\n'
    '    "other_environmental": {\n'
    '      "additional_metrics": {},\n'
    '      "environmental_goals": [],\n'
    '      "environmental_initiatives": [],\n'
    '      "environmental_partnerships": []\n'
    '    }\n'
    '  }\n'
    "}\n"
    
    "INSTRUCTIONS:\n"
    "- For each category, populate 'details' with ORIGINAL TEXT SEGMENTS exactly as they appear in the source text\n"
    "- If no specific data is found for a category, leave it as empty arrays/objects\n"
    "- Extract ALL environmental-related information from the text\n"
    "- Be comprehensive and thorough in your analysis\n"
    "- Focus on finding actual numbers, percentages, and specific metrics mentioned in the text\n"
    "- IMPORTANT: Every number you find should go into the 'metrics' section\n"
    "- CRITICAL: For emissions, always check if the text mentions 'net' vs 'gross' and use the appropriate metric name\n"
    "- CRITICAL: Distinguish between traditional Scope 3 and Scope 3+ concepts\n"
    "- CRITICAL: Avoid creating duplicate metrics - use only ONE metric name per value\n"
    "- CRITICAL: DO NOT summarize or modify original text in details - use exact text segments\n"
    "- CRITICAL: Preserve original text exactly, only replacing underscores with spaces for JSON format\n"
    "- CRITICAL: Preserve ALL unit prefixes (giga, million, billion, etc.) exactly as mentioned in text\n"
    
    f"TEXT TO ANALYZE:\n{chr(10).join(all_text_content)}\n"  # Use ALL text segments
    "Provide your analysis in the exact JSON format specified above."
)

# FIXED Comprehensive LLM prompt for detailed Social (S) analysis
social_prompt = (
    f"You are an expert ESG analyst specializing in Social (S) data extraction and categorization. "
    f"Analyze the following text content from the {year} Sustainability Report and extract ALL social information. "
    f"Provide a comprehensive, detailed categorization of social data including both quantitative metrics and qualitative information. "
    
    "CRITICAL REQUIREMENTS:\n"
    "1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS from the text\n"
    "2. Populate 'metrics' objects with actual numerical values (e.g., 'employee_count': '1.6 million', 'diversity_percentage': '45%')\n"
    "3. Include both quantitative data (numbers, percentages, metrics) and qualitative information (goals, strategies, initiatives)\n"
    "4. Preserve exact numbers and units as mentioned in the text\n"
    "5. Your response MUST be a single, valid JSON object and nothing else\n"
    "6. If you find numbers in the text, ALWAYS put them in the 'metrics' section\n"
    "7. CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly as mentioned in text\n"
    "8. CRITICAL: DO NOT SUMMARIZE OR MODIFY ORIGINAL TEXT in details\n"
    "9. CRITICAL: Details should contain ORIGINAL TEXT SEGMENTS exactly as they appear\n"
    "10. CRITICAL: Preserve ALL unit prefixes (million, billion, etc.) exactly as mentioned in text\n"
    
    "EXAMPLE METRICS FORMAT:\n"
    '  "metrics": {\n'
    '    "total_employees": "1.6 million",\n'
    '    "diversity_percentage": "45%",\n'
    '    "training_hours": "2.5 million hours"\n'
    '  }\n'
    
    "CATEGORIZE INTO THESE DETAILED SECTIONS:\n"
    "{\n"
    '  "social_comprehensive": {\n'
    '    "diversity_inclusion": {\n'
    '      "gender_diversity": {"details": [], "metrics": {}},\n'
    '      "racial_ethnic_diversity": {"details": [], "metrics": {}},\n'
    '      "leadership_diversity": {"details": [], "metrics": {}},\n'
    '      "inclusion_initiatives": [],\n'
    '      "diversity_goals": []\n'
    '    },\n'
    '    "employee_development": {\n'
    '      "training_programs": {"details": [], "metrics": {}},\n'
    '      "education_support": {"details": [], "metrics": {}},\n'
    '      "career_development": {"details": [], "metrics": {}},\n'
    '      "skill_building": {"details": [], "metrics": {}},\n'
    '      "mentorship_programs": []\n'
    '    },\n'
    '    "health_safety": {\n'
    '      "workplace_safety": {"details": [], "metrics": {}},\n'
    '      "health_benefits": {"details": [], "metrics": {}},\n'
    '      "mental_health": {"details": [], "metrics": {}},\n'
    '      "wellness_programs": [],\n'
    '      "safety_goals": []\n'
    '    },\n'
    '    "compensation_benefits": {\n'
    '      "pay_equity": {"details": [], "metrics": {}},\n'
    '      "benefits_programs": {"details": [], "metrics": {}},\n'
    '      "minimum_wage": {"details": [], "metrics": {}},\n'
    '      "compensation_goals": []\n'
    '    },\n'
    '    "community_engagement": {\n'
    '      "community_investment": {"details": [], "metrics": {}},\n'
    '      "volunteer_programs": {"details": [], "metrics": {}},\n'
    '      "philanthropy": {"details": [], "metrics": {}},\n'
    '      "local_partnerships": [],\n'
    '      "community_goals": []\n'
    '    },\n'
    '    "human_rights": {\n'
    '      "supply_chain_labor": {"details": [], "metrics": {}},\n'
    '      "forced_labor_prevention": {"details": [], "metrics": {}},\n'
    '      "child_labor_prevention": {"details": [], "metrics": {}},\n'
    '      "human_rights_assessments": [],\n'
    '      "remediation_efforts": []\n'
    '    },\n'
    '    "other_social": {\n'
    '      "additional_metrics": {},\n'
    '      "social_goals": [],\n'
    '      "social_initiatives": [],\n'
    '      "social_partnerships": []\n'
    '    }\n'
    '  }\n'
    "}\n"
    
    "INSTRUCTIONS:\n"
    "- For each category, populate 'details' with descriptive information and 'metrics' with specific numbers/percentages\n"
    "- If no specific data is found for a category, leave it as empty arrays/objects\n"
    "- Extract ALL social-related information from the text\n"
    "- Be comprehensive and thorough in your analysis\n"
    "- Focus on finding actual numbers, percentages, and specific metrics mentioned in the text\n"
    "- IMPORTANT: Every number you find should go into the 'metrics' section\n"
    
    f"TEXT TO ANALYZE:\n{chr(10).join(all_text_content)}\n"  # Use ALL text segments
    "Provide your analysis in the exact JSON format specified above."
)

# Comprehensive LLM prompt for detailed Governance (G) analysis
governance_prompt = (
    f"You are an expert ESG analyst specializing in Governance (G) data extraction and categorization. "
    f"Analyze the following text content from Amazon's {year} Sustainability Report and extract ALL governance information. "
    f"Provide a comprehensive, detailed categorization of governance data including both quantitative metrics and qualitative information. "
    
    "CRITICAL REQUIREMENTS:\n"
    "1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS from the text\n"
    "2. Populate 'metrics' objects with actual numerical values (e.g., 'board_independence': '80%', 'compliance_rate': '99.5%')\n"
    "3. Include both quantitative data (numbers, percentages, metrics) and qualitative information (goals, strategies, initiatives)\n"
    "4. Preserve exact numbers and units as mentioned in the text\n"
    "5. Your response MUST be a single, valid JSON object and nothing else\n"
    "6. If you find numbers in the text, ALWAYS put them in the 'metrics' section\n"
    
    "EXAMPLE METRICS FORMAT:\n"
    '  "metrics": {\n'
    '    "board_independence": "80%",\n'
    '    "compliance_rate": "99.5%",\n'
    '    "ethics_training_hours": "2.5 million hours"\n'
    '  }\n'
    
    "CATEGORIZE INTO THESE DETAILED SECTIONS:\n"
    "{\n"
    '  "governance_comprehensive": {\n'
    '    "board_governance": {\n'
    '      "board_composition": {"details": [], "metrics": {}},\n'
    '      "board_independence": {"details": [], "metrics": {}},\n'
    '      "board_diversity": {"details": [], "metrics": {}},\n'
    '      "board_oversight": [],\n'
    '      "board_goals": []\n'
    '    },\n'
    '    "executive_compensation": {\n'
    '      "compensation_structure": {"details": [], "metrics": {}},\n'
    '      "performance_metrics": {"details": [], "metrics": {}},\n'
    '      "equity_compensation": {"details": [], "metrics": {}},\n'
    '      "compensation_goals": []\n'
    '    },\n'
    '    "ethics_compliance": {\n'
    '      "code_of_conduct": {"details": [], "metrics": {}},\n'
    '      "compliance_programs": {"details": [], "metrics": {}},\n'
    '      "whistleblower_protection": {"details": [], "metrics": {}},\n'
    '      "ethics_training": [],\n'
    '      "compliance_goals": []\n'
    '    },\n'
    '    "risk_management": {\n'
    '      "risk_assessment": {"details": [], "metrics": {}},\n'
    '      "risk_mitigation": {"details": [], "metrics": {}},\n'
    '      "esg_risk_integration": {"details": [], "metrics": {}},\n'
    '      "risk_goals": []\n'
    '    },\n'
    '    "transparency_disclosure": {\n'
    '      "reporting_framework": {"details": [], "metrics": {}},\n'
    '      "stakeholder_engagement": {"details": [], "metrics": {}},\n'
    '      "disclosure_practices": {"details": [], "metrics": {}},\n'
    '      "transparency_goals": []\n'
    '    },\n'
    '    "other_governance": {\n'
    '      "additional_metrics": {},\n'
    '      "governance_goals": [],\n'
    '      "governance_initiatives": [],\n'
    '      "governance_partnerships": []\n'
    '    }\n'
    '  }\n'
    "}\n"
    
    "INSTRUCTIONS:\n"
    "- For each category, populate 'details' with descriptive information and 'metrics' with specific numbers/percentages\n"
    "- If no specific data is found for a category, leave it as empty arrays/objects\n"
    "- Extract ALL governance-related information from the text\n"
    "- Be comprehensive and thorough in your analysis\n"
    "- Focus on finding actual numbers, percentages, and specific metrics mentioned in the text\n"
    "- IMPORTANT: Every number you find should go into the 'metrics' section\n"
    
    f"TEXT TO ANALYZE:\n{chr(10).join(all_text_content)}\n"  # Use ALL text segments
    "Provide your analysis in the exact JSON format specified above."
)

# Helper function to extract response text
def extract_response_text(response):
    response_text = None
    
    # Debug: Print the response structure
    print(f"[DEBUG] Response type: {type(response)}")
    print(f"[DEBUG] Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
    
    if isinstance(response, dict):
        # Handle OpenAI-compatible format
        if 'choices' in response and len(response['choices']) > 0:
            choice = response['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                response_text = choice['message']['content']
            elif 'content' in choice:
                response_text = choice['content']
        # Handle DashScope format (fallback)
        elif 'output' in response and 'choices' in response['output']:
            choice = response['output']['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                response_text = choice['message']['content']
            elif 'content' in choice:
                response_text = choice['content']
    
    elif isinstance(response, list):
        # Handle list format
        for choice in response:
            if isinstance(choice, dict):
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content']
                    break
                elif 'content' in choice:
                    response_text = choice['content']
                    break
    
    if response_text is None:
        print("[ERROR] Could not find 'content' in LLM response. Full response:")
        print(response)
        return None
    
    # Clean the response to make it valid JSON
    if response_text.strip().startswith("```json"):
        response_text = response_text.strip()[7:-3].strip()
    
    # Find the main JSON object and ignore any extra text
    try:
        start = response_text.index("{")
        end = response_text.rindex("}") + 1
        response_text = response_text[start:end]
    except ValueError:
        pass  # No JSON object found
    
    return response_text

# Process Environmental (E) data
print("PROCESSING: Processing Environmental (E) data...")
environmental_summary_json = process_chunks_with_llm(text_chunks, environmental_prompt, "Environmental")

# Process Social (S) data
print("PROCESSING: Processing Social (S) data...")
social_summary_json = process_chunks_with_llm(text_chunks, social_prompt, "Social")

# Process Governance (G) data
print("PROCESSING: Processing Governance (G) data...")
governance_summary_json = process_chunks_with_llm(text_chunks, governance_prompt, "Governance")

# Save output with comprehensive ESG data
result = {
    "environmental_comprehensive_analysis": environmental_summary_json,
    "social_comprehensive_analysis": social_summary_json,
    "governance_comprehensive_analysis": governance_summary_json,
    "analysis_metadata": {
        "total_text_segments_analyzed": len(all_text_content),
        "segments_used_in_analysis": len(all_text_content),
        "analysis_type": "comprehensive_esg_categorization",
        "extraction_method": "all_text_content_inclusion",
        "esg_areas_analyzed": ["environmental", "social", "governance"]
    }
}

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Comprehensive ESG analysis saved to {OUTPUT_JSON}")
print(f"SUCCESS: Analysis included {len(all_text_content)} text segments for detailed categorization")
print("SUCCESS: All data is from actual LLM analysis - no mock data used") 