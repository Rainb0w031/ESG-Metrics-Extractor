"""LLM-enhanced segmentation."""

from typing import Dict, Any, Optional
from pathlib import Path
from prompter.prompt import BasePromptModel
from prompter.items import OllamaChatItem
from ..core.base import BaseSegmenter
from ..core.models import LLMAnalysisResponse
from .basic_segmenter import BasicSegmenter


class LLMSegmenter(BaseSegmenter, BasePromptModel):
    """
    Creates text segments using LLM enhancement.
    Falls back to basic segmentation if LLM fails.
    """
    
    def __init__(self, which_model: str, system_prompt: Optional[str] = None):
        """
        Initialize LLM segmenter.
        
        Args:
            which_model: LLM model to use
            system_prompt: Optional custom system prompt
        """
        BasePromptModel.__init__(
            self,
            which_model=which_model,
            system_prompt=system_prompt or self._get_default_system_prompt()
        )
        
        self.basic_segmenter = BasicSegmenter()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for segment analysis."""
        return """You are an expert document analyzer. Your task is to extract and structure 
        content from documents, ensuring accuracy and completeness in the extraction process. 
        You will categorize text segments into appropriate roles and provide structured output."""
    
    def create_segment(self, text: str, page_num: int, segment_num: int, 
                      total_segments: int) -> Dict[str, Any]:
        """
        Create a segment using LLM enhancement.
        
        Args:
            text: Text content
            page_num: Page number
            segment_num: Segment number on the page
            total_segments: Total segments on the page
            
        Returns:
            Segment dictionary
        """
        try:
            prompt = self._create_segment_analysis_prompt(text, page_num, segment_num, total_segments)
            
            if self.which_model.startswith('ollama'):
                chat_item = OllamaChatItem(messages=[{"role": "user", "content": prompt}])
            else:
                from prompter.items import NonOpenAIChatItem
                chat_item = NonOpenAIChatItem(messages=[{"role": "user", "content": prompt}])
            
            response = self.chat(chat_item, json_model=LLMAnalysisResponse)
            
            if hasattr(response, 'text_segments') and response.text_segments:
                segment_analysis = response.text_segments[0]
                
                return {
                    'segment_id': f"page_{page_num}_segment_{segment_num}",
                    'text': text,
                    'role': segment_analysis.get('role', 'content'),
                    'chunk_index': segment_num - 1,
                    'confidence': segment_analysis.get('confidence', 0.8),
                    'position': segment_analysis.get('position', 'middle'),
                    'importance': segment_analysis.get('importance', 'medium'),
                    'context': segment_analysis.get('context', f'Segment on page {page_num}')
                }
            
            # Fallback to basic segmentation
            return self.basic_segmenter.create_segment(text, page_num, segment_num, total_segments)
                
        except Exception as e:
            print(f"[WARN] LLM segmentation failed: {e}. Using basic segmentation.")
            return self.basic_segmenter.create_segment(text, page_num, segment_num, total_segments)
    
    def _create_segment_analysis_prompt(self, text: str, page_num: int, segment_num: int, total_segments: int) -> str:
        """Create prompt for segment analysis."""
        return f"""Analyze this text segment from PDF page {page_num} (segment {segment_num}/{total_segments}) and provide detailed metadata.

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
- Role: What type of content this is (headline, content, methodology, etc.)
- Confidence: How certain you are about the classification (0.0-1.0)
- Position: Where this text appears in the document flow
- Importance: How important this content is to the document
- Context: What this text represents or describes

Respond only with valid JSON."""

