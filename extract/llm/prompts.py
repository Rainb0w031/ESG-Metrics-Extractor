"""Prompt templates for LLM-based text analysis.

Matches the reference implementation's _create_chunk_prompt() method.
"""

from typing import List


def create_chunk_prompt(chunk_text: str, page_number: int, 
                        chunk_num: int, total_chunks: int) -> str:
    """
    Create a prompt for analyzing a text chunk.
    
    Matches the reference implementation's _create_chunk_prompt() method.
    
    Args:
        chunk_text: Text content of the chunk
        page_number: Page number
        chunk_num: Chunk number (1-indexed)
        total_chunks: Total chunks for this page
        
    Returns:
        Prompt string for LLM
    """
    return f"""Analyze this text chunk from PDF page {page_number} (chunk {chunk_num}/{total_chunks}) and identify text roles. Keep response minimal and valid JSON.

TEXT: {chunk_text}

Return ONLY valid JSON:
{{
    "text_segments": [
        {{
            "text": "text content",
            "role": "headline|subheadline|content|caption|footnote|list_item|table_content|metadata|quote",
            "confidence": 0.9,
            "position": "start",
            "importance": "high",
            "context": "brief description"
        }}
    ],
    "main_topics": ["topic1"]
}}"""


def create_page_analysis_prompt(page_text: str, page_number: int) -> str:
    """
    Create a prompt for analyzing an entire page.
    
    Args:
        page_text: Full text content of the page
        page_number: Page number
        
    Returns:
        Prompt string for LLM
    """
    return f"""Analyze the following text from PDF page {page_number} and identify text segments with their roles.

TEXT:
{page_text}

For each segment, identify:
1. The text content
2. Its role (headline, content, list_item, caption, footnote, etc.)
3. Confidence level (0.0-1.0)
4. Position in document (start, middle, end)
5. Importance level (high, medium, low)
6. Brief context description

Return ONLY valid JSON with this structure:
{{
    "page_number": {page_number},
    "text_segments": [
        {{
            "text": "segment text",
            "role": "content|headline|list_item|caption|footnote|table_content|metadata|quote|executive_summary|methodology|results|conclusion",
            "confidence": 0.85,
            "position": "middle",
            "importance": "medium",
            "context": "Description of what this segment represents"
        }}
    ],
    "main_topics": ["topic1", "topic2"],
    "page_summary": "Brief summary of page content"
}}"""


def create_segment_analysis_prompt(text: str, page_number: int,
                                   segment_num: int, total_segments: int) -> str:
    """
    Create a prompt for analyzing a single text segment.
    
    Args:
        text: Text content
        page_number: Page number
        segment_num: Segment number (1-indexed)
        total_segments: Total segments
        
    Returns:
        Prompt string for LLM
    """
    return f"""Analyze this text segment from PDF page {page_number} (segment {segment_num}/{total_segments}) and provide detailed metadata.

Text: "{text}"

Please provide a JSON response with the following structure:
{{
    "text_segments": [
        {{
            "text": "{text}",
            "role": "headline|subheadline|content|caption|footnote|list_item|table_content|metadata|quote|executive_summary|methodology|results|conclusion|appendix",
            "confidence": 0.0-1.0,
            "position": "start|middle|end",
            "importance": "high|medium|low",
            "context": "brief description of what this text represents"
        }}
    ],
    "main_topics": ["topic1", "topic2"]
}}

Focus on:
- Role: What type of content this is
- Confidence: How certain you are about the classification (0.0-1.0)
- Position: Where this text appears in the document flow
- Importance: How important this content is to the document
- Context: What this text represents or describes

Respond only with valid JSON."""


# Text role definitions for system prompts
TEXT_ROLE_DESCRIPTIONS = {
    'headline': 'Main titles, chapter titles, section headers',
    'subheadline': 'Subsection headers, minor titles',
    'content': 'Main body text, paragraphs, descriptions',
    'caption': 'Figure captions, table captions, image descriptions',
    'footnote': 'Footnotes, endnotes, references',
    'list_item': 'Bullet points, numbered lists, list items',
    'table_content': 'Table data, tabular information',
    'metadata': 'Page numbers, dates, document metadata',
    'quote': 'Quotations, highlighted text, callouts',
    'executive_summary': 'Executive summaries, key findings',
    'methodology': 'Methodology sections, procedures',
    'results': 'Results sections, findings, data',
    'conclusion': 'Conclusions, recommendations',
    'appendix': 'Appendix content, supplementary information'
}


def get_system_prompt() -> str:
    """
    Get system prompt for text role analysis.
    
    Returns:
        System prompt string
    """
    roles_desc = "\n".join(f"- {role}: {desc}" for role, desc in TEXT_ROLE_DESCRIPTIONS.items())
    
    return f"""You are an expert document analyzer specializing in PDF text extraction and classification.

Your task is to analyze text segments and classify them into appropriate roles:

{roles_desc}

Guidelines:
1. Be precise in role classification
2. Provide confidence scores reflecting certainty
3. Consider context when determining importance
4. Keep responses minimal and valid JSON
5. Focus on the actual content, not formatting artifacts
"""
