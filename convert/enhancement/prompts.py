"""Prompt templates for LLM-based metric enhancement."""


def get_name_enhancement_prompt(metrics_text: str, company: str, year: str) -> str:
    """Get prompt for metric name enhancement."""
    return f"""You are an expert ESG analyst tasked with converting raw metric names into clear, direct, and meaningful descriptions.

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
{metrics_text}

Provide the enhanced metric names in JSON format:
{{
  "enhanced_metrics": [
    {{
      "original_name": "original_metric_name",
      "enhanced_name": "enhanced_metric_name"
    }}
  ]
}}"""


def get_category_generation_prompt(metrics_text: str, company: str, year: str) -> str:
    """Get prompt for category generation."""
    return f"""You are an expert ESG analyst tasked with categorizing ESG metrics into detailed categories.

COMPANY: {company}
YEAR: {year}

TASK: Categorize the following ESG metrics into detailed, specific categories that would be useful for dashboard filtering and analysis.

CATEGORY GUIDELINES:
- Use the format "ESG Area - Specific Category"
- ESG Areas: E (Environmental), S (Social), G (Governance)
- Be specific and descriptive
- Examples: "E - carbon emissions", "S - employee development", "G - board governance"

METRICS TO CATEGORIZE:
{metrics_text}

Provide the categories in JSON format:
{{
  "categorized_metrics": [
    {{
      "metric_name": "metric_name",
      "category": "E - specific_category"
    }}
  ]
}}"""


def get_importance_analysis_prompt(metrics_text: str, company: str, year: str, batch_size: int) -> str:
    """Get prompt for importance analysis with double materiality."""
    return f"""You are an ESG analyst evaluating the importance of sustainability metrics for {company} in {year}.

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
{metrics_text}

Provide your analysis in this exact format:
Metric 1: [High/Medium/Low] - [brief reasoning]
Metric 2: [High/Medium/Low] - [brief reasoning]
...
Metric {batch_size}: [High/Medium/Low] - [brief reasoning]

Focus on practical business impact and stakeholder relevance."""


def get_combined_processing_prompt(metrics_text: str, company: str, year: str, batch_size: int) -> str:
    """Get combined prompt for name enhancement, category generation, and importance analysis."""
    return f"""You are an expert ESG analyst processing sustainability metrics for {company} in {year}.

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
{metrics_text}

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
Metric {batch_size}:
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
