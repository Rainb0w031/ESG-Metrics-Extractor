#!/usr/bin/env python3
"""
Enhanced Structured Content Producer
Integrates error detection and fixing with optimized chunking for better performance
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

try:
    from pdf_content_extractor_ultra_robust import UltraRobustPDFContentExtractor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure pdf_content_extractor_ultra_robust.py is in the current directory")
    sys.exit(1)

class EnhancedStructuredContentProducer:
    def __init__(self, optimized_chunking=True):
        """Initialize the enhanced producer with optimized settings"""
        self.optimized_chunking = optimized_chunking
        self.extractor = UltraRobustPDFContentExtractor()
        
        # Optimize chunking settings for better performance
        if optimized_chunking:
            self.extractor.config['max_text_length'] = 500  # Increased from 400 for better efficiency
            self.extractor.config['chunk_size'] = 320  # Increased from 250 for better efficiency
            print("🔧 Using optimized chunking settings for faster processing")
    
    def identify_failed_pages(self, structured_content: Dict[str, Any]) -> List[int]:
        """Identify pages with errors in structured content"""
        failed_pages = []
        
        for page in structured_content.get("pages", []):
            page_num = page.get("page_number", 0)
            
            # Check for various error conditions
            has_error = (
                "error" in page and page["error"] or
                not page.get("text_segments") or
                len(page.get("text_segments", [])) == 0 or
                len(page.get("original_text", "")) < 50 or
                "JSON parsing error" in str(page.get("error", "")) or
                "Analysis error" in str(page.get("error", ""))
            )
            
            if has_error:
                failed_pages.append(page_num)
                print(f"   ❌ Page {page_num}: {page.get('error', 'Empty or malformed content')}")
        
        return failed_pages
    
    def fix_failed_pages(self, pdf_file: Path, failed_pages: List[int], 
                        existing_content: Dict[str, Any]) -> Dict[str, Any]:
        """Fix specific failed pages using ultra-robust extractor"""
        if not failed_pages:
            return existing_content
        
        print(f"🔧 Fixing {len(failed_pages)} failed pages...")
        
        # Process failed pages in batches for efficiency
        batch_size = 5
        for i in range(0, len(failed_pages), batch_size):
            batch = failed_pages[i:i + batch_size]
            print(f"📄 Processing batch {i//batch_size + 1}: pages {batch}")
            
            try:
                # Process the batch
                result = self.extractor.process_pdf(
                    file_path=pdf_file,
                    page_range=(min(batch) - 1, max(batch) - 1),  # Convert to 0-based
                    resume_from=min(batch)
                )
                
                if result and "pages" in result:
                    # Replace failed pages with fixed ones
                    for fixed_page in result["pages"]:
                        page_num = fixed_page.get("page_number", 0)
                        
                        # Find and replace the page in existing content
                        for j, page in enumerate(existing_content.get("pages", [])):
                            if page.get("page_number") == page_num:
                                existing_content["pages"][j] = fixed_page
                                print(f"      ✅ Fixed page {page_num}")
                                break
                
                # Small delay between batches to avoid overwhelming the API
                if i + batch_size < len(failed_pages):
                    time.sleep(2)
                    
            except Exception as e:
                print(f"      ❌ Error processing batch {batch}: {e}")
        
        return existing_content
    
    def validate_and_enhance_content(self, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content quality and enhance if needed"""
        print("🔍 Validating content quality...")
        
        total_pages = len(structured_content.get("pages", []))
        successful_pages = 0
        failed_pages = 0
        
        for page in structured_content.get("pages", []):
            if page.get("error") or not page.get("text_segments"):
                failed_pages += 1
            else:
                successful_pages += 1
        
        print(f"📊 Quality Report:")
        print(f"   Total pages: {total_pages}")
        print(f"   Successful: {successful_pages}")
        print(f"   Failed: {failed_pages}")
        print(f"   Success rate: {(successful_pages/total_pages)*100:.1f}%")
        
        return structured_content
    
    def produce_structured_content(self, pdf_file: Path, output_file: Path, 
                                company: str = "Amazon", year: str = "2021") -> bool:
        """Produce structured content with integrated error detection and fixing"""
        
        print(f"🚀 Enhanced Structured Content Production")
        print(f"📄 PDF: {pdf_file}")
        print(f"📄 Output: {output_file}")
        print(f"🏢 Company: {company}")
        print(f"📅 Year: {year}")
        
        # Step 1: Initial extraction
        print("\n📋 Step 1: Initial PDF extraction...")
        try:
            result = self.extractor.process_pdf(file_path=pdf_file)
            
            if not result or "pages" not in result:
                print("❌ Initial extraction failed")
                return False
            
            print(f"✅ Initial extraction completed: {len(result['pages'])} pages")
            
        except Exception as e:
            print(f"❌ Initial extraction error: {e}")
            return False
        
        # Step 2: Identify failed pages
        print("\n🔍 Step 2: Identifying failed pages...")
        failed_pages = self.identify_failed_pages(result)
        
        if failed_pages:
            print(f"⚠️ Found {len(failed_pages)} failed pages: {failed_pages}")
            
            # Step 3: Fix failed pages
            print("\n🔧 Step 3: Fixing failed pages...")
            result = self.fix_failed_pages(pdf_file, failed_pages, result)
            
            # Step 4: Re-validate after fixing
            print("\n🔍 Step 4: Re-validating after fixes...")
            remaining_failed = self.identify_failed_pages(result)
            
            if remaining_failed:
                print(f"⚠️ {len(remaining_failed)} pages still have issues: {remaining_failed}")
            else:
                print("✅ All pages successfully fixed!")
        else:
            print("✅ No failed pages detected!")
        
        # Step 5: Final validation and enhancement
        print("\n📊 Step 5: Final validation and enhancement...")
        result = self.validate_and_enhance_content(result)
        
        # Step 6: Save the final result
        print(f"\n💾 Step 6: Saving enhanced structured content...")
        try:
            # Create the output directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created/verified directory: {output_file.parent}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Enhanced structured content saved to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Enhanced Structured Content Producer")
    parser.add_argument("--pdf-file", required=True, help="Path to the PDF file")
    parser.add_argument("--output-file", required=True, help="Path to save the structured content")
    parser.add_argument("--company", default="Amazon", help="Company name")
    parser.add_argument("--year", default="2021", help="Report year")
    parser.add_argument("--optimized", action="store_true", help="Use optimized chunking for faster processing")
    
    args = parser.parse_args()
    
    # Create producer with optimized settings
    producer = EnhancedStructuredContentProducer(optimized_chunking=args.optimized)
    
    # Produce structured content
    success = producer.produce_structured_content(
        pdf_file=Path(args.pdf_file),
        output_file=Path(args.output_file),
        company=args.company,
        year=args.year
    )
    
    if success:
        print("\n🎉 Enhanced structured content production completed successfully!")
    else:
        print("\n❌ Enhanced structured content production failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 