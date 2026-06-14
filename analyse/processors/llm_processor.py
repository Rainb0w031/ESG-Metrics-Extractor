"""
LLM-based chunk processor for ESG analysis.

Handles LLM calls, response extraction, JSON parsing, and error handling.
Extracted from ESGLLMAnalyzer._process_chunk_with_llm() and _extract_response_text().
"""

import json
import time
from typing import Dict, Any, Optional, List
from loguru import logger

from prompter.items import OllamaChatItem, NonOpenAIChatItem

from .base_processor import BaseProcessor, ProcessorConfig


class LLMProcessor(BaseProcessor):
    """
    LLM-based chunk processor.
    
    Features:
    - LLM calls via prompter infrastructure
    - Multiple response format support (list, OpenAI, DashScope)
    - Automatic JSON extraction and parsing
    - Retry logic with exponential backoff
    - Comprehensive error handling and logging
    
    Maintains quality standards from reference implementation:
    - Conservative temperature (0.2)
    - Generous timeout (120s)
    - Proper error handling
    - JSON validation
    """
    
    def __init__(self, analyzer, config: ProcessorConfig = None):
        """
        Initialize LLM processor.
        
        Args:
            analyzer: Analyzer instance (has .chat() method from BasePromptModel)
            config: Processor configuration
        """
        super().__init__(config)
        self.analyzer = analyzer  # Has .which_model and .chat() method
        logger.info(f"LLM processor initialized for model: {self.analyzer.which_model}")
    
    def process(self, prompt: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Process prompt with LLM.
        
        Features:
        - Automatic retry on failure
        - Multiple response format support
        - JSON extraction and parsing
        - Comprehensive logging
        
        Args:
            prompt: Prompt to process
            analysis_type: Type of analysis ("comprehensive", "environmental", etc.)
        
        Returns:
            Dict containing analysis result, or None if processing failed
        """
        for attempt in range(self.config.max_retries):
            try:
                result = self._process_single_attempt(prompt, analysis_type)
                if result is not None:
                    return result
                
                # Failed, retry if attempts remaining
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (attempt + 1)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                    time.sleep(delay)
            
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} raised exception: {e}")
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (attempt + 1)
                    logger.warning(f"Retrying in {delay}s...")
                    time.sleep(delay)
        
        logger.error(f"All {self.config.max_retries} attempts failed for {analysis_type}")
        return None
    
    def _process_single_attempt(self, prompt: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Process a single LLM attempt.
        
        Args:
            prompt: Prompt to process
            analysis_type: Type of analysis
        
        Returns:
            Result dict or None if failed
        """
        try:
            # Create messages with system and user content
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert ESG analyst that only responds with comprehensive, detailed JSON categorizations of {analysis_type.lower()} data. Your response must be valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Use the appropriate chat item based on the model type
            if self.analyzer.which_model.startswith('ollama'):
                chat_item = OllamaChatItem(messages=messages)
            else:
                chat_item = NonOpenAIChatItem(messages=messages)
            
            logger.debug(f"Sending prompt to LLM (model={self.analyzer.which_model})")
            
            # Use prompter's chat method
            response = self.analyzer.chat(chat_item)
            
            # Log response structure for debugging
            logger.debug(f"Response type: {type(response)}")
            if isinstance(response, list) and len(response) > 0:
                logger.debug(f"Response list length: {len(response)}")
                logger.debug(f"Last message role: {response[-1].get('role', 'N/A')}")
                logger.debug(f"Last message content preview: {response[-1].get('content', '')[:100]}...")
            
            # Extract response text
            response_text = self._extract_response_text(response)
            if response_text is None:
                logger.warning(f"Failed to extract {analysis_type} response text")
                return None
            
            logger.debug(f"Extracted text length: {len(response_text)} chars")
            logger.debug(f"Extracted text preview: {response_text[:200]}...")
            
            # Parse JSON response
            try:
                chunk_result = json.loads(response_text)
                logger.debug(f"Successfully parsed {analysis_type} JSON with {len(chunk_result)} top-level keys")
                return chunk_result
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse {analysis_type} JSON: {e}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}...")
                
                if self.config.enable_retry_on_json_error:
                    logger.warning("JSON parse error - will retry")
                    return None
                else:
                    raise
        
        except Exception as e:
            logger.error(f"LLM processing failed for {analysis_type}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _extract_response_text(self, response) -> Optional[str]:
        """
        Extract response text from LLM response.
        
        Supports multiple response formats:
        1. Prompter list format (default)
        2. OpenAI-compatible dict format
        3. DashScope dict format
        
        Also handles:
        - Markdown JSON code blocks (```json)
        - Extra text around JSON object
        
        Args:
            response: LLM response in various formats
        
        Returns:
            Extracted and cleaned JSON string, or None if extraction failed
        """
        response_text = None
        
        logger.debug(f"Extracting from response type: {type(response)}")
        
        # Format 1: Prompter list format
        if isinstance(response, list):
            # Find the last assistant message
            for message in reversed(response):
                if isinstance(message, dict) and message.get('role') == 'assistant':
                    response_text = message.get('content')
                    logger.debug("Extracted from prompter list format")
                    break
            
            if response_text is None:
                logger.error("Could not find assistant message in response list")
                logger.error(f"Response structure: {response}")
                return None
        
        # Format 2: Dict formats (OpenAI, DashScope, etc.)
        elif isinstance(response, dict):
            # OpenAI-compatible format
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content']
                    logger.debug("Extracted from OpenAI format")
                elif 'content' in choice:
                    response_text = choice['content']
                    logger.debug("Extracted from OpenAI format (alt)")
            
            # DashScope format
            elif 'output' in response and 'choices' in response['output']:
                choice = response['output']['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content']
                    logger.debug("Extracted from DashScope format")
                elif 'content' in choice:
                    response_text = choice['content']
                    logger.debug("Extracted from DashScope format (alt)")
        
        # Could not extract
        if response_text is None:
            logger.error("Could not find 'content' in LLM response")
            logger.error(f"Full response: {response}")
            return None
        
        # Clean the response
        response_text = self._clean_response_text(response_text)
        
        return response_text
    
    def _clean_response_text(self, response_text: str) -> Optional[str]:
        """
        Clean response text to extract valid JSON.
        
        Handles:
        - Markdown JSON code blocks (```json ... ```)
        - Extra text before/after JSON object
        
        Args:
            response_text: Raw response text
        
        Returns:
            Cleaned JSON string, or None if no valid JSON found
        """
        # Remove markdown JSON code blocks
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:]  # Remove ```json
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            logger.debug("Removed markdown JSON code block")
        
        # Find the main JSON object (from first { to last })
        try:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            response_text = response_text[start:end]
            logger.debug(f"Extracted JSON object: {len(response_text)} chars")
        except ValueError:
            logger.error(f"Could not find JSON object in response")
            logger.error(f"Response text (first 200 chars): {response_text[:200]}...")
            return None
        
        return response_text
    
    def process_batch(self, prompts: List[str], analysis_type: str) -> List[Optional[Dict[str, Any]]]:
        """
        Process multiple prompts sequentially.
        
        Note: This is sequential processing. For parallel processing,
        use ParallelProcessor (future implementation).
        
        Args:
            prompts: List of prompts to process
            analysis_type: Type of analysis
        
        Returns:
            List of results (None for failed items)
        """
        results = []
        total = len(prompts)
        
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"Processing batch item {i}/{total}")
            result = self.process(prompt, analysis_type)
            results.append(result)
            
            # Add delay between requests (except for last)
            if i < total:
                time.sleep(self.config.retry_delay)
        
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"Batch complete: {success_count}/{total} successful")
        
        return results

