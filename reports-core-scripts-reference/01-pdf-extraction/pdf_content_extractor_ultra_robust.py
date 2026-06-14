import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import PyPDF2
import fitz
import pdfplumber
import re
from typing import Dict, List, Any, Optional
import argparse
import traceback
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import get_api_config
except ImportError:
    # Try importing from reports-indexing-main config
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports-indexing-main'))
    from config import get_api_config

class UltraRobustPDFContentExtractor:
    """Ultra-robust PDF content extractor with minimal chunks and aggressive error handling."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the ultra-robust PDF content extractor."""
        # Use centralized config
        config = get_api_config('qwen')
        
        # Optimized configuration for better performance
        self.config = {
            'api_key': api_key or config['api_key'],
            'base_url': base_url or config['api_base'],
            'model': config['model'],  # Use model from config
            'max_tokens': 2000,
            'temperature': 0.0,
            'max_retries': 3,
            'retry_delay': 2,
            'timeout': 60,
            'max_text_length': 500,  # Increased from 400 for better efficiency
            'chunk_size': 320,  # Increased from 250 for better efficiency
            'max_chunks_per_page': 20,  # Limit chunks to avoid overwhelming API
            'batch_delay': 1  # Delay between batches
        }
        
        # Text role categories
        self.text_roles = {
            'headline': 'Main titles, chapter titles, section headers',
            'subheadline': 'Subsection headers, minor titles',
            'content': 'Main body text, paragraphs, descriptions',
            'caption': 'Figure captions, table captions, image descriptions',
            'footnote': 'Footnotes, endnotes, references',
            'list_item': 'Bullet points, numbered lists, list items',
            'table_content': 'Table data, tabular information',
            'metadata': 'Page numbers, dates, document metadata',
            'quote': 'Quotations, highlighted text, callouts',
            'code': 'Code snippets, technical specifications',
            'formula': 'Mathematical formulas, equations',
            'contact_info': 'Contact information, addresses, phone numbers',
            'disclaimer': 'Legal disclaimers, terms, conditions',
            'executive_summary': 'Executive summaries, key findings',
            'methodology': 'Methodology sections, procedures',
            'results': 'Results sections, findings, data',
            'conclusion': 'Conclusions, recommendations',
            'appendix': 'Appendix content, supplementary information'
        }
    
    def extract_text_from_pdf(self, file_path: Path, method: str = 'auto') -> Dict[str, Any]:
        """Extract text from PDF using multiple methods."""
        print(f"[DEBUG] Entering extract_text_from_pdf with file_path={file_path}, method={method}")
        text_data = {
            'pages': [],
            'metadata': {},
            'extraction_method': method,
            'success': False,
            'error': None
        }
        
        try:
            if method == 'auto' or method == 'pypdf2':
                text_data = self._extract_with_pypdf2(file_path)
                if text_data['success']:
                    return text_data
            
            if method == 'auto' or method == 'pymupdf':
                text_data = self._extract_with_pymupdf(file_path)
                if text_data['success']:
                    return text_data
            
            if method == 'auto' or method == 'pdfplumber':
                text_data = self._extract_with_pdfplumber(file_path)
                if text_data['success']:
                    return text_data
            
            text_data['error'] = 'All text extraction methods failed'
            return text_data
            
        except Exception as e:
            text_data['error'] = str(e)
            return text_data
    
    def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Extract text using PyPDF2."""
        text_data = {
            'pages': [],
            'metadata': {},
            'extraction_method': 'pypdf2',
            'success': False,
            'error': None
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if pdf_reader.metadata:
                    text_data['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text and len(text.strip()) > self.config['max_text_length']:
                        text_data['pages'].append({
                            'page_number': page_num + 1,
                            'text': text.strip(),
                            'char_count': len(text),
                            'word_count': len(text.split())
                        })
                
                text_data['success'] = True
                return text_data
                
        except Exception as e:
            text_data['error'] = f"PyPDF2 extraction failed: {str(e)}"
            return text_data
    
    def _extract_with_pymupdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text using PyMuPDF."""
        text_data = {
            'pages': [],
            'metadata': {},
            'extraction_method': 'pymupdf',
            'success': False,
            'error': None
        }
        
        try:
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = doc.metadata
            text_data['metadata'] = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', '')
            }
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text and len(text.strip()) > self.config['max_text_length']:
                    text_data['pages'].append({
                        'page_number': page_num + 1,
                        'text': text.strip(),
                        'char_count': len(text),
                        'word_count': len(text.split())
                    })
            
            doc.close()
            text_data['success'] = True
            return text_data
            
        except Exception as e:
            text_data['error'] = f"PyMuPDF extraction failed: {str(e)}"
            return text_data
    
    def _extract_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Extract text using pdfplumber."""
        text_data = {
            'pages': [],
            'metadata': {},
            'extraction_method': 'pdfplumber',
            'success': False,
            'error': None
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    text_data['metadata'] = {
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', ''),
                        'creation_date': pdf.metadata.get('CreationDate', ''),
                        'modification_date': pdf.metadata.get('ModDate', '')
                    }
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text and len(text.strip()) > self.config['max_text_length']:
                        text_data['pages'].append({
                            'page_number': page_num + 1,
                            'text': text.strip(),
                            'char_count': len(text),
                            'word_count': len(text.split())
                        })
            
            text_data['success'] = True
            return text_data
            
        except Exception as e:
            text_data['error'] = f"pdfplumber extraction failed: {str(e)}"
            return text_data
    
    def analyze_text_roles_with_llm(self, text_content: str, page_number: int, retry_count: int = 0) -> Dict[str, Any]:
        """Analyze text roles using LLM with optimized chunking."""
        if retry_count >= self.config['max_retries']:
            return self._create_fallback_response(page_number, text_content, "Max retries exceeded")
        
        try:
            # Clean the text content
            cleaned_text = self._clean_text_content(text_content)
            
            # Split into optimized chunks
            chunks = self._chunk_text_content(cleaned_text, page_number)
            print(f"  Split page {page_number} into {len(chunks)} chunks")
            
            if not chunks:
                return self._create_fallback_response(page_number, text_content, "No valid chunks created")
            
            # Process chunks with batch delays
            all_segments = []
            for i, chunk in enumerate(chunks):
                print(f"  Processing chunk {i+1}/{len(chunks)} for page {page_number}")
                
                # Create chunk-specific prompt
                prompt = self._create_chunk_prompt(chunk, page_number, i+1, len(chunks))
                
                # Make API call for this chunk
                result = self._make_api_call_with_retry(prompt, page_number)
                
                if result and isinstance(result, list):
                    all_segments.extend(result)
                else:
                    print(f"    ⚠️ Chunk {i+1} failed, using fallback")
                    all_segments.append({
                        "text": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                        "role": "content",
                        "confidence": 0.5,
                        "position": "middle",
                        "importance": "medium",
                        "context": "Fallback content due to processing error"
                    })
                
                # Add delay between chunks to avoid overwhelming API
                if i < len(chunks) - 1:
                    time.sleep(self.config['batch_delay'])
            
            # Combine all segments
            if all_segments:
                return {
                    "page_number": page_number,
                    "text_segments": all_segments,
                    "page_summary": f"Page {page_number} processed with {len(all_segments)} segments",
                    "main_topics": [seg.get("context", "general") for seg in all_segments[:5]],
                    "document_section": "content"
                }
            else:
                return self._create_fallback_response(page_number, text_content, "No segments generated")
                
        except Exception as e:
            print(f"  ❌ Error analyzing page {page_number}: {e}")
            if retry_count < self.config['max_retries']:
                print(f"  🔄 Retrying page {page_number} (attempt {retry_count + 1})")
                time.sleep(self.config['retry_delay'])
                return self.analyze_text_roles_with_llm(text_content, page_number, retry_count + 1)
            else:
                return self._create_fallback_response(page_number, text_content, str(e))
    
    def _chunk_text_content(self, text_content: str, page_number: int) -> List[str]:
        """Split text content into manageable chunks."""
        max_chars_per_chunk = self.config['chunk_size']
        max_chunks = self.config['max_chunks_per_page']
        
        if len(text_content) <= max_chars_per_chunk:
            return [text_content]
        
        # Split by sentences first, then by words if needed
        sentences = text_content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars_per_chunk:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    if len(chunks) >= max_chunks:
                        break
                current_chunk = sentence + ". "
        
        # Add the last chunk if it exists
        if current_chunk and len(chunks) < max_chunks:
            chunks.append(current_chunk.strip())
        
        # If we still have too many chunks, merge some
        if len(chunks) > max_chunks:
            merged_chunks = []
            for i in range(0, len(chunks), 2):
                if i + 1 < len(chunks):
                    merged_chunks.append(chunks[i] + " " + chunks[i + 1])
                else:
                    merged_chunks.append(chunks[i])
            chunks = merged_chunks[:max_chunks]
        
        return chunks
    
    def _create_chunk_prompt(self, chunk_text: str, page_number: int, chunk_num: int, total_chunks: int) -> str:
        """Create a prompt for analyzing a text chunk."""
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
    
    def _make_api_call_with_retry(self, prompt: str, page_number: int, retry_count: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Make API call with retry logic."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config['model'], # Use model from config
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config['temperature'],
                "max_tokens": self.config['max_tokens']
            }
            
            # Use the base URL directly (no additional path)
            response = requests.post(
                self.config['base_url'],
                headers=headers,
                json=data,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Debug: Print the raw LLM response
                print(f"    📝 Raw LLM response for chunk: {content[:200]}...")
                
                # Parse the response
                analysis = self._parse_llm_response_ultra_robust(content, page_number)
                
                if analysis and isinstance(analysis, dict) and 'text_segments' in analysis:
                    print(f"    ✅ Successfully parsed {len(analysis['text_segments'])} segments")
                    return analysis['text_segments']  # Return just the text_segments list
                else:
                    print(f"    ❌ Parsing failed - analysis: {analysis}")
                    # Retry if parsing failed
                    if retry_count < self.config['max_retries']:
                        print(f"  Retrying chunk due to parsing error")
                        time.sleep(self.config['retry_delay'])
                        return self._make_api_call_with_retry(prompt, page_number, retry_count + 1)
                    else:
                        return None
            else:
                error_msg = f"LLM API error: {response.status_code}"
                print(f"❌ API Error Details:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                print(f"   Request URL: {self.config['base_url']}")
                print(f"   Request Data Length: {len(str(data))}")
                print(f"   Prompt Length: {len(prompt)}")
                
                if retry_count < self.config['max_retries']:
                    print(f"  Retrying chunk due to API error")
                    time.sleep(self.config['retry_delay'])
                    return self._make_api_call_with_retry(prompt, page_number, retry_count + 1)
                else:
                    return None
                    
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            if retry_count < self.config['max_retries']:
                print(f"  Retrying chunk due to exception")
                time.sleep(self.config['retry_delay'])
                return self._make_api_call_with_retry(prompt, page_number, retry_count + 1)
            else:
                return None
    
    def _clean_text_content(self, text: str) -> str:
        """Clean text content to remove problematic characters."""
        # Remove or replace problematic characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'["""]', '"', text)  # Normalize quotes
        text = re.sub(r"[''']", "'", text)  # Normalize apostrophes
        text = text.strip()
        return text
    
    def _parse_llm_response_ultra_robust(self, content: str, page_number: int) -> Optional[Dict[str, Any]]:
        """Ultra-robust JSON parsing with multiple aggressive fallback methods."""
        
        # Method 1: Direct JSON parsing
        try:
            parsed = json.loads(content.strip())
            if isinstance(parsed, dict) and 'text_segments' in parsed:
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Method 2: Remove markdown code blocks
        try:
            cleaned_content = content
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            parsed = json.loads(cleaned_content.strip())
            if isinstance(parsed, dict) and 'text_segments' in parsed:
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Method 3: Find JSON object boundaries
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)
                if isinstance(parsed, dict) and 'text_segments' in parsed:
                    return parsed
        except json.JSONDecodeError:
            pass
        
        # Method 4: Fix common JSON issues aggressively
        try:
            # Fix unescaped quotes in strings
            fixed_content = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', content)
            # Fix missing quotes around property names
            fixed_content = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_content)
            # Fix trailing commas
            fixed_content = re.sub(r',(\s*[}\]])', r'\1', fixed_content)
            parsed = json.loads(fixed_content)
            if isinstance(parsed, dict) and 'text_segments' in parsed:
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Method 5: Create a simple fallback response
        try:
            # If we can't parse the JSON, create a simple response with the text as content
            return {
                "text_segments": [
                    {
                        "text": content[:500] + "..." if len(content) > 500 else content,
                        "role": "content",
                        "confidence": 0.7,
                        "position": "middle",
                        "importance": "medium",
                        "context": "LLM response converted to content"
                    }
                ],
                "main_topics": ["general_content"],
                "page_summary": "Content processed with fallback parsing"
            }
        except Exception:
            pass
        
        return None
    
    def _create_fallback_response(self, page_number: int, text_content: str, error_msg: str = "") -> Dict[str, Any]:
        """Create a minimal fallback response when all else fails."""
        return {
            "page_number": page_number,
            "error": f"Failed after {self.config['max_retries']} attempts. {error_msg}",
            "text_segments": [
                {
                    "text": text_content[:200] + "..." if len(text_content) > 200 else text_content,
                    "role": "content",
                    "confidence": 0.5,
                    "position": "start",
                    "importance": "medium",
                    "context": "Fallback content due to processing error"
                }
            ],
            "page_summary": "Page content could not be fully analyzed due to processing errors",
            "main_topics": ["processing_error"],
            "document_section": "unknown"
        }
    
    def process_pdf(self, file_path: Path, output_path: Optional[Path] = None, page_range: Optional[tuple] = None, resume_from: Optional[int] = None) -> Dict[str, Any]:
        """Process a PDF file with ultra-robust error handling."""
        print(f"🔍 Processing PDF: {file_path.name}")
        
        # Extract text from PDF
        print(f"  Extracting text...")
        text_data = self.extract_text_from_pdf(file_path)
        
        if not text_data['success']:
            print(f"  ❌ Text extraction failed: {text_data['error']}")
            return text_data
        
        print(f"  ✅ Extracted {len(text_data['pages'])} pages using {text_data['extraction_method']}")
        
        # Determine pages to process
        pages_to_process = text_data['pages']
        if page_range:
            start, end = page_range
            pages_to_process = pages_to_process[start:end+1]
        
        # Resume from specific page if provided
        if resume_from:
            pages_to_process = [p for p in pages_to_process if p['page_number'] >= resume_from]
            print(f"  📄 Resuming from page {resume_from}")
        
        # Load existing results if resuming
        existing_results = []
        if resume_from and output_path and output_path.exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_results = [p for p in existing_data.get('pages', []) if p.get('page_number', 0) < resume_from]
                    print(f"  📄 Loaded {len(existing_results)} existing pages")
            except Exception as e:
                print(f"  ⚠️ Could not load existing results: {e}")
        
        # Initialize structured content
        structured_content = {
            'file_info': {
                'filename': file_path.name,
                'file_size_mb': file_path.stat().st_size / (1024 * 1024),
                'extraction_method': text_data['extraction_method'],
                'total_pages': len(text_data['pages']),
                'processing_date': datetime.now().isoformat(),
                'version': '3.0'  # Ultra-robust version
            },
            'metadata': text_data['metadata'],
            'pages': existing_results,
            'document_summary': {
                'total_segments': 0,
                'role_distribution': {},
                'main_topics': [],
                'document_sections': []
            }
        }
        
        # Process pages with ultra-robust error handling
        total_segments = 0
        role_distribution = {}
        successful_pages = 0
        failed_pages = 0
        
        for i, page_data in enumerate(pages_to_process):
            page_num = page_data['page_number']
            print(f"    Analyzing page {page_num} ({i+1}/{len(pages_to_process)})...")
            
            # Analyze page with LLM
            page_analysis = self.analyze_text_roles_with_llm(
                page_data['text'], 
                page_num
            )
            
            # Add original page data
            page_analysis['original_text'] = page_data['text']
            page_analysis['char_count'] = page_data['char_count']
            page_analysis['word_count'] = page_data['word_count']
            
            # Check if analysis was successful
            if 'error' in page_analysis and page_analysis['error']:
                print(f"      ❌ Page {page_num} failed: {page_analysis['error']}")
                failed_pages += 1
            else:
                print(f"      ✅ Page {page_num} processed successfully")
                successful_pages += 1
            
            structured_content['pages'].append(page_analysis)
            
            # Update statistics
            if 'text_segments' in page_analysis:
                total_segments += len(page_analysis['text_segments'])
                
                for segment in page_analysis['text_segments']:
                    role = segment.get('role', 'unknown')
                    role_distribution[role] = role_distribution.get(role, 0) + 1
            
            # Add main topics and document sections
            if 'main_topics' in page_analysis:
                structured_content['document_summary']['main_topics'].extend(
                    page_analysis['main_topics']
                )
            
            if 'document_section' in page_analysis:
                section = page_analysis['document_section']
                if section not in structured_content['document_summary']['document_sections']:
                    structured_content['document_summary']['document_sections'].append(section)
            
            # Save progress periodically
            if (i + 1) % 5 == 0:  # Save more frequently
                self._save_progress(structured_content, output_path)
                print(f"      💾 Progress saved ({i+1}/{len(pages_to_process)} pages)")
            
            # Delay between pages to avoid rate limiting
            time.sleep(2)  # Longer delay
        
        # Update final statistics
        structured_content['document_summary']['total_segments'] = total_segments
        structured_content['document_summary']['role_distribution'] = role_distribution
        
        # Remove duplicates from main topics
        structured_content['document_summary']['main_topics'] = list(set(
            structured_content['document_summary']['main_topics']
        ))
        
        # Save final result
        if output_path is None:
            output_path = file_path.parent / f"{file_path.stem}_ultra_robust_structured_content.json"
        
        self._save_progress(structured_content, output_path)
        
        print(f"  ✅ Processing complete!")
        print(f"    📊 Successful pages: {successful_pages}")
        print(f"    ❌ Failed pages: {failed_pages}")
        print(f"    💾 Saved to: {output_path.name}")
        
        return structured_content
    
    def _save_progress(self, structured_content: Dict[str, Any], output_path: Path):
        """Save progress to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structured_content, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ❌ Error saving progress: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ultra-Robust PDF Content Extractor")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--page-range", help="Page range to process, e.g., '1-10' (1-based, inclusive)")
    parser.add_argument("--resume-from", type=int, help="Resume processing from specific page number")
    parser.add_argument("--api-key", help="API key for LLM service")
    parser.add_argument("--base-url", help="Base URL for LLM service")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return
    
    # Initialize extractor
    extractor = UltraRobustPDFContentExtractor(
        api_key=args.api_key,
        base_url=args.base_url
    )
    
    # Parse page range
    page_range = None
    if args.page_range:
        start, end = [int(x) for x in args.page_range.split("-")]
        page_range = (start-1, end-1)  # Convert to 0-based
    
    # Process PDF
    if args.resume_from:
        result = extractor.process_pdf(input_path, output_path, page_range, args.resume_from)
    else:
        result = extractor.process_pdf(input_path, output_path, page_range)
    
    if result:
        print(f"✅ Processing completed successfully!")
    else:
        print(f"❌ Processing failed!")

if __name__ == "__main__":
    main() 