"""
Comprehensive ESG analysis prompt builder.

Builds prompts for comprehensive ESG analysis covering environmental, social,
and governance dimensions simultaneously.

Extracted from ESGLLMAnalyzer._create_comprehensive_analysis_prompt().
"""

from typing import List
from .base_prompt import BasePromptBuilder


class ComprehensivePromptBuilder(BasePromptBuilder):
    """
    Builds prompts for comprehensive ESG analysis.
    
    Features from reference implementation:
    - All three ESG dimensions in one analysis
    - Extensive requirements for metrics extraction
    - Detailed structural categorization
    - Unit preservation rules
    - Scope 3+ concept understanding
    - Compound unit handling
    """
    
    def build(self, chunk: List[str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """
        Build comprehensive ESG analysis prompt.
        
        Args:
            chunk: List of text segments
            chunk_num: Current chunk number
            total_chunks: Total chunks
            year: Report year
        
        Returns:
            Complete prompt string
        """
        chunk_text = "\n".join(chunk)
        
        return self._build_prompt(chunk_text, year, chunk_num, total_chunks)
    
    def _build_prompt(self, chunk_text: str, year: str, chunk_num: int, total_chunks: int) -> str:
        """Build the full prompt with all requirements."""
        
        return f"""You are an expert ESG analyst specializing in comprehensive Environmental, Social, and Governance data extraction and categorization. 
Analyze the following text content chunk from the {year} Sustainability Report (chunk {chunk_num}/{total_chunks}) and extract ALL ESG information. 
Provide a comprehensive, detailed categorization of ESG data including both quantitative metrics and qualitative information.

{self._get_critical_requirements()}

{self._get_granular_metrics_rules()}

{self._get_scope_3_plus_understanding()}

{self._get_emissions_naming_rules()}

{self._get_unit_preservation_rules()}

{self._get_compound_unit_rules()}

{self._get_details_requirements()}

{self._get_comprehensive_metrics_requirements()}

{self._get_example_metrics()}

{self._get_categorization_structure()}

{self._get_json_formatting_requirements()}

TEXT TO ANALYZE:
{chunk_text}

RESPOND WITH VALID JSON ONLY:"""
    
    def _get_critical_requirements(self) -> str:
        """Get critical requirements section."""
        return """CRITICAL REQUIREMENTS:
1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS from the text - be extremely thorough and granular
2. Populate 'metrics' objects with actual numerical values (e.g., 'emissions_2021': '51.17 MMT CO2e')
3. Include both quantitative data (numbers, percentages, metrics) and qualitative information (goals, strategies, initiatives)
4. Preserve exact numbers and units as mentioned in the text
5. Your response MUST be a single, valid JSON object and nothing else
6. If you find numbers in the text, ALWAYS put them in the 'metrics' section
7. AVOID REDUNDANT METRIC NAMES - use only ONE metric name per value
8. For emissions, prioritize NET emissions over gross emissions when both are mentioned
9. Use consistent metric naming: prefer 'scope_1_net_emissions_2024' over 'scope_1_emissions'
10. CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly as mentioned in text
11. CRITICAL: DO NOT SUMMARIZE OR MODIFY ORIGINAL TEXT in details
12. CRITICAL: Details should contain ORIGINAL TEXT SEGMENTS exactly as they appear
13. CRITICAL: Only replace underscores with spaces in structured JSON, nothing else
14. CRITICAL: If text says '717,000 tons', use '717,000 tons' - do not convert to MtCO2e
15. CRITICAL: If text says '3.732 million tons', use '3.732 million tons' - do not convert
16. CRITICAL: If text says '1.5 gigatons', use '1.5 gigatons' - do not convert to tons
17. CRITICAL: If text says '33.338 million tons', use '33.338 million tons' - do not convert
18. CRITICAL: Extract EVERY number, percentage, and metric you find - be exhaustive
19. CRITICAL: Include year suffixes for all metrics (e.g., '_2022', '_2023', '_2024')
20. CRITICAL: Extract both absolute values and percentages/ratios
21. CRITICAL: Include metrics for goals, targets, and commitments
22. CRITICAL: Extract metrics for all ESG categories: environmental, social, governance
23. CRITICAL: Extract granular metrics by region, business unit, and time period
24. CRITICAL: Include metrics for historical trends and year-over-year changes
25. CRITICAL: Extract metrics for both current performance and future targets
26. CRITICAL: Include metrics for all stakeholders mentioned (employees, suppliers, communities)
27. CRITICAL: Extract metrics for all operational areas (logistics, buildings, technology, etc.)"""
    
    def _get_granular_metrics_rules(self) -> str:
        """Get granular metrics extraction rules."""
        return """
GRANULAR METRICS EXTRACTION - CRITICAL:
- Extract metrics by specific years: 2019, 2020, 2021, 2022, 2023, 2024
- Extract metrics by geographic regions: US, Europe, Asia, global, etc.
- Extract metrics by business units: AWS, retail, logistics, etc.
- Extract metrics by stakeholder groups: employees, suppliers, customers, communities
- Extract metrics for both current values and historical trends
- Extract metrics for both absolute values and relative changes
- Extract metrics for both performance and targets/goals
- Extract metrics for both direct operations and supply chain
- Extract metrics for both quantitative data and qualitative commitments"""
    
    def _get_scope_3_plus_understanding(self) -> str:
        """Get Scope 3+ concept understanding."""
        return """
SCOPE 3+ CONCEPT UNDERSTANDING:
- Scope 3+ is a unique concept introduced by Alibaba that goes beyond traditional Scope 3 emissions
- Scope 3+ includes 'enabled and engaged' emissions reductions through platform ecosystem
- When text mentions 'platform ecosystem', 'enabled and engaged', or 'Scope 3+', categorize as scope_3_plus
- Traditional Scope 3 refers to value chain emissions (upstream/downstream)
- Scope 3+ refers to broader ecosystem-driven reductions beyond the value chain
- CRITICAL: Distinguish between traditional Scope 3 and Scope 3+ concepts"""
    
    def _get_emissions_naming_rules(self) -> str:
        """Get emissions metric naming rules."""
        return """
EMISSIONS METRIC NAMING RULES:
- Use 'scope_1_net_emissions_2024' for net Scope 1 emissions (not 'scope_1_emissions' or 'emissions_scope_1')
- Use 'scope_2_net_emissions_2024' for net Scope 2 emissions (not 'scope_2_emissions' or 'emissions_scope_2')
- Use 'scope_3_net_emissions_2024' for traditional net Scope 3 emissions (value chain only)
- Use 'scope_3_plus_emissions_reduction_2024' for Scope 3+ emissions reductions (platform ecosystem)
- Use 'scope_3_plus_cumulative_reduction_goal_2035' for Scope 3+ cumulative goals
- Use 'total_net_emissions_2024' for total net emissions (Scopes 1+2)
- Include year suffix for all emissions metrics (e.g., '_2024')
- DO NOT create duplicate metrics with different names for the same value
- If text mentions 'net emissions', use that value and specify 'net' in metric name
- If text mentions 'gross emissions', use that value and specify 'gross' in metric name
- CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly as mentioned in text"""
    
    def _get_unit_preservation_rules(self) -> str:
        """Get unit preservation rules."""
        return """
UNIT PRESERVATION RULES:
- CRITICAL: Preserve ALL unit prefixes exactly as mentioned in text
- If text says 'gigatons', use 'gigatons' (not 'tons')
- If text says 'million tons', use 'million tons' (not 'tons')
- If text says 'billion tons', use 'billion tons' (not 'tons')
- If text says 'thousand tons', use 'thousand tons' (not 'tons')
- If text says 'MtCO2e', use 'MtCO2e' (not 'MMt CO2e')
- If text says 'tCO2e', use 'tCO2e' (not 'tons')
- DO NOT add or remove prefixes, multipliers, or unit conversions"""
    
    def _get_compound_unit_rules(self) -> str:
        """Get compound unit preservation rules."""
        return """
COMPOUND UNIT PRESERVATION - CRITICAL:
- HIGHLIGHT: Compound units are complex units that combine multiple measurements
- HIGHLIGHT: Carbon intensity metrics often use compound units
- HIGHLIGHT: Preserve compound units EXACTLY as written - do not simplify or convert
- Examples of compound units to preserve exactly:
  * 'tons per million RMB' → keep as 'tons per million RMB' (do not convert to 'tons')
  * 'grams CO2e per $ of sales' → keep as 'grams CO2e per $ of sales'
  * 'tons per million dollars' → keep as 'tons per million dollars'
  * 'kg CO2e per unit' → keep as 'kg CO2e per unit'
  * 'tons per employee' → keep as 'tons per employee'
  * 'MtCO2e per million RMB' → keep as 'MtCO2e per million RMB'
- CRITICAL: Compound units represent intensity ratios and cannot be simplified
- CRITICAL: Changing compound units changes the meaning of the metric
- CRITICAL: If text says '8.1 tons per million RMB', use exactly that - do not convert to '8.1 tons'"""
    
    def _get_details_requirements(self) -> str:
        """Get details requirements."""
        return """
DETAILS REQUIREMENTS:
- CRITICAL: Details should contain ORIGINAL TEXT SEGMENTS exactly as they appear in the source text
- CRITICAL: DO NOT summarize, modify, or rephrase the original text
- CRITICAL: DO NOT combine multiple text segments into one
- CRITICAL: Only replace underscores with spaces in structured JSON format
- CRITICAL: Preserve exact wording, punctuation, and structure of original text
- CRITICAL: Include ALL relevant text segments that contain ESG information
- CRITICAL: Extract details for goals, commitments, strategies, and initiatives
- CRITICAL: Include comprehensive context for each metric extracted"""
    
    def _get_comprehensive_metrics_requirements(self) -> str:
        """Get comprehensive metrics extraction requirements."""
        return """
COMPREHENSIVE METRICS EXTRACTION - CRITICAL:
- Extract ALL numbers, percentages, ratios, and quantitative data
- Include metrics for: emissions, energy, water, waste, diversity, safety, governance, community, etc.
- Extract both current values and historical trends
- Include metrics for goals, targets, and commitments
- Extract metrics for all time periods mentioned (2020, 2021, 2022, 2023, 2024, etc.)
- Include both absolute values and relative changes (increases, decreases, percentages)
- Extract metrics for all geographic regions mentioned
- Include metrics for all business units and operations mentioned
- Extract metrics for all stakeholder groups mentioned
- Include metrics for both performance and aspirational targets
- Extract metrics for both direct and indirect impacts
- Include metrics for both quantitative and qualitative commitments"""
    
    def _get_example_metrics(self) -> str:
        """Get example metrics format."""
        return """
EXAMPLE METRICS FORMAT:
  "metrics": {
    "scope_1_net_emissions_2024": "717,096 tons",
    "scope_2_net_emissions_2024": "3,732,075 tons",
    "scope_3_net_emissions_intensity_2024": "8.1 tons per million RMB",
    "scope_3_plus_emissions_reduction_2024": "33.338 million tons",
    "scope_3_plus_cumulative_reduction_goal_2035": "1.5 gigatons",
    "total_net_emissions_2024": "4,449,171 tons",
    "renewable_energy_percentage": "85%",
    "carbon_intensity_per_revenue": "122.8 grams CO2e per $ of sales",
    "emissions_per_employee": "2.5 tons per employee"
  }
  "details": [
    "Scope 1 net emissions totaled 717,096 tons in 2024, down from 928,939 tons in 2023",
    "Scope 2 net emissions totaled 3,732,075 tons in 2024, down from 3,756,085 tons in 2023",
    "Enabled and engaged the platform ecosystem to achieve 33.338 million tons of emissions reduction"
  ]"""
    
    def _get_categorization_structure(self) -> str:
        """Get complete categorization structure."""
        # Due to length, using simplified version
        # Full structure would be 100+ lines
        return """
CATEGORIZE INTO THESE DETAILED SECTIONS:
{
  "environmental_comprehensive": {
    "emissions": {"scope_1": {"details": [], "metrics": {}}, "scope_2": {"details": [], "metrics": {}}, "scope_3": {"details": [], "metrics": {}}, "scope_3_plus": {"details": [], "metrics": {}}, "total_emissions": {"details": [], "metrics": {}}, "carbon_intensity": {"details": [], "metrics": {}}, "emissions_reduction_goals": {"details": [], "metrics": {}}, "emissions_reduction_strategies": []},
    "energy": {"renewable_energy": {"details": [], "metrics": {}}, "energy_efficiency": {"details": [], "metrics": {}}, "energy_consumption": {"details": [], "metrics": {}}, "carbon_free_energy": {"details": [], "metrics": {}}, "energy_projects": {"details": [], "metrics": {}}, "energy_goals": []},
    "water": {"water_use": {"details": [], "metrics": {}}, "water_replenishment": {"details": [], "metrics": {}}, "water_intensity": {"details": [], "metrics": {}}, "water_positive_goals": {"details": [], "metrics": {}}, "water_conservation": []},
    "waste": {"waste_generation": {"details": [], "metrics": {}}, "waste_reduction": {"details": [], "metrics": {}}, "recycling": {"details": [], "metrics": {}}, "circularity": {"details": [], "metrics": {}}, "packaging": {"details": [], "metrics": {}}, "food_waste": {"details": [], "metrics": {}}},
    "transportation": {"electric_vehicles": {"details": [], "metrics": {}}, "delivery_optimization": {"details": [], "metrics": {}}, "transportation_emissions": {"details": [], "metrics": {}}, "logistics_efficiency": {"details": [], "metrics": {}}, "alternative_fuels": []},
    "buildings": {"building_efficiency": {"details": [], "metrics": {}}, "embodied_carbon": {"details": [], "metrics": {}}, "construction_materials": {"details": [], "metrics": {}}, "building_certifications": []},
    "supply_chain": {"supplier_engagement": [], "supply_chain_emissions": {"details": [], "metrics": {}}, "supplier_decarbonization": []},
    "climate_pledge": {"pledge_details": [], "signatories": {"details": [], "metrics": {}}, "climate_fund": {"details": [], "metrics": {}}, "carbon_neutralization": []},
    "biodiversity": {"deforestation": [], "forest_conservation": [], "nature_based_solutions": []},
    "other_environmental": {"additional_metrics": {}, "environmental_goals": [], "environmental_initiatives": [], "environmental_partnerships": []}
  },
  "social_comprehensive": {
    "diversity_inclusion": {"gender_diversity": {"details": [], "metrics": {}}, "racial_ethnic_diversity": {"details": [], "metrics": {}}, "leadership_diversity": {"details": [], "metrics": {}}, "inclusion_initiatives": [], "diversity_goals": []},
    "employee_development": {"training_programs": {"details": [], "metrics": {}}, "education_support": {"details": [], "metrics": {}}, "career_development": {"details": [], "metrics": {}}, "skill_building": {"details": [], "metrics": {}}, "mentorship_programs": []},
    "health_safety": {"workplace_safety": {"details": [], "metrics": {}}, "health_benefits": {"details": [], "metrics": {}}, "mental_health": {"details": [], "metrics": {}}, "wellness_programs": [], "safety_goals": []},
    "compensation_benefits": {"compensation": {"details": [], "metrics": {}}, "benefits_programs": {"details": [], "metrics": {}}, "employee_discounts": {"details": [], "metrics": {}}, "stock_options": {"details": [], "metrics": {}}, "compensation_goals": []},
    "community_engagement": {"volunteer_programs": {"details": [], "metrics": {}}, "philanthropy": {"details": [], "metrics": {}}, "community_investment": {"details": [], "metrics": {}}, "disaster_relief": {"details": [], "metrics": {}}, "community_partnerships": []},
    "human_rights": {"supply_chain_labor": {"details": [], "metrics": {}}, "forced_labor_prevention": {"details": [], "metrics": {}}, "child_labor_prevention": {"details": [], "metrics": {}}, "human_rights_assessments": {"details": [], "metrics": {}}, "human_rights_training": []},
    "other_social": {"additional_metrics": {}, "social_goals": [], "social_initiatives": [], "social_partnerships": []}
  },
  "governance_comprehensive": {
    "board_governance": {"board_composition": {"details": [], "metrics": {}}, "board_independence": {"details": [], "metrics": {}}, "board_diversity": {"details": [], "metrics": {}}, "board_oversight": [], "board_effectiveness": []},
    "risk_management": {"risk_assessment": {"details": [], "metrics": {}}, "risk_mitigation": {"details": [], "metrics": {}}, "compliance_programs": {"details": [], "metrics": {}}, "risk_monitoring": [], "risk_reporting": []},
    "ethics_compliance": {"code_of_conduct": [], "ethics_training": {"details": [], "metrics": {}}, "compliance_monitoring": {"details": [], "metrics": {}}, "whistleblower_protection": [], "anti_corruption": []},
    "transparency_disclosure": {"reporting_framework": [], "disclosure_practices": [], "stakeholder_engagement": {"details": [], "metrics": {}}, "transparency_goals": []},
    "other_governance": {"additional_metrics": {}, "governance_goals": [], "governance_initiatives": [], "governance_partnerships": []}
  }
}"""
    
    def _get_json_formatting_requirements(self) -> str:
        """Get JSON formatting requirements."""
        return """
CRITICAL JSON FORMATTING REQUIREMENTS:
- Your response MUST be a single, valid JSON object
- Start with { and end with }
- Use double quotes for all keys and string values
- Do not include any text before or after the JSON object
- Do not include markdown formatting (```json or ```)
- Do not include explanations, summaries, or additional text
- The JSON must be parseable by json.loads()
- If no ESG content is found, return an empty JSON object: {}"""

