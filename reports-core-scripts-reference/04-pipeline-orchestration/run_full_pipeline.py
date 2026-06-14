#!/usr/bin/env python3
"""
Enhanced ESG Pipeline - Complete Processing Chain
Integrates all existing scripts without redundancy:
1. PDF Download (optional)
2. Text Extraction & Structured Content
3. LLM Quantitative Analysis
4. Dashboard Analysis Conversion
5. Dashboard Integration
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path
import time
from datetime import datetime

# Fix import paths to work from pipeline directory
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def run_pdf_download(company, year, output_dir):
    """Find PDF in ESG reports folder with flexible naming patterns"""
    # Look in the ESG reports folder
    esg_reports_dir = parent_dir / "ESG reports"
    
    if not esg_reports_dir.exists():
        print(f"❌ ESG reports folder not found: {esg_reports_dir}")
        return None
    
    # Try different naming patterns for the PDF
    possible_names = [
        f"{year}_ESG_Report_{year}_-_Amazon_S3.pdf",
        f"{year}_ESG_Report_{year}_-_Amazon_S3_ultra_robust_structured_content.json",
        f"{year}_{year}_Amazon_Sustainability_Report.pdf",
        f"{year}-amazon-sustainability-report-aws-summary.pdf",
        f"{year}_Amazon_Sustainability_Report.pdf",
        f"{year}_ESG_Report.pdf",
        f"{year}_Sustainability_Report.pdf"
    ]
    
    # Also try to find any PDF containing the year
    year_pattern = f"{year}*.pdf"
    year_matches = list(esg_reports_dir.glob(year_pattern))
    
    # Check each possible name
    for name in possible_names:
        pdf_path = esg_reports_dir / name
        if pdf_path.exists():
            print(f"✅ Found PDF: {pdf_path}")
            return str(pdf_path)
    
    # If no exact match, try year pattern matches
    if year_matches:
        pdf_path = year_matches[0]
        print(f"✅ Found PDF by year pattern: {pdf_path}")
        return str(pdf_path)
    
    # List available PDFs for debugging
    available_pdfs = list(esg_reports_dir.glob("*.pdf"))
    print(f"⚠️ No PDF found for year {year}")
    print(f"Available PDFs in ESG reports folder:")
    for pdf in available_pdfs:
        print(f"  - {pdf.name}")
    
    return None

def run_pdf_extraction(pdf_path, output_json, year):
    """Run enhanced PDF extraction with error detection and fixing"""
    if os.path.exists(output_json):
        print(f"⏭️ Skipping PDF extraction, output already exists: {output_json}")
        return output_json
    
    print(f"📄 Running enhanced PDF extraction...")
    
    try:
        # Use the enhanced structured content producer
        from enhanced_structured_content_producer import EnhancedStructuredContentProducer
        
        # Create producer with optimized settings
        producer = EnhancedStructuredContentProducer(optimized_chunking=True)
        
        # Extract with integrated error detection and fixing
        success = producer.produce_structured_content(
            pdf_file=Path(pdf_path),
            output_file=Path(output_json),
            company="Amazon",
            year=year
        )
        
        if success:
            print(f"✅ Enhanced PDF extraction completed: {output_json}")
            return output_json
        else:
            print(f"❌ Enhanced PDF extraction failed")
            return None
        
    except Exception as e:
        print(f"❌ Enhanced PDF extraction failed: {e}")
        return None

def run_llm_analysis(input_json, output_json):
    """Run LLM analysis using existing quantitative_llm_analysis_clean.py"""
    if os.path.exists(output_json):
        print(f"⏭️ Skipping LLM analysis, output already exists: {output_json}")
        return output_json
    
    print(f"🤖 Running LLM analysis...")
    
    try:
        # Use absolute paths for the script
        script_path = parent_dir / "quantitative_llm_analysis_clean.py"
        cmd = [sys.executable, str(script_path), str(input_json), str(output_json)]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=parent_dir)
        print(f"✅ LLM analysis completed: {output_json}")
        return output_json
        
    except subprocess.CalledProcessError as e:
        print(f"❌ LLM analysis failed: {e}")
        print(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ LLM analysis failed: {e}")
        return None

def run_dashboard_conversion(analysis_json, dashboard_json, company, year):
    """Run enhanced dashboard conversion with integrated metric enhancement and categorization"""
    if os.path.exists(dashboard_json):
        print(f"⏭️ Skipping dashboard conversion, output already exists: {dashboard_json}")
        return dashboard_json
    
    print(f"🔄 Running enhanced dashboard conversion...")
    
    try:
        # Use the enhanced conversion script
        from convert_comprehensive_to_dashboard_enhanced import convert_comprehensive_to_dashboard_enhanced
        
        # Convert with integrated enhancement and categorization
        result = convert_comprehensive_to_dashboard_enhanced(
            input_file=str(analysis_json),
            output_file=str(dashboard_json),
            company=company,
            year=year
        )
        
        if result:
            print(f"✅ Enhanced dashboard conversion completed: {dashboard_json}")
            return dashboard_json
        else:
            print(f"❌ Enhanced dashboard conversion failed")
            return None
            
    except Exception as e:
        print(f"❌ Enhanced dashboard conversion failed: {e}")
        return None

def run_dashboard_integration(dashboard_json, company, year):
    """Run enhanced dashboard integration directly to categorized dashboard"""
    print(f"🔄 Running enhanced dashboard integration...")
    
    try:
        # Use the enhanced integration script
        from integrate_esg_data_to_categorized_dashboard import integrate_esg_data_to_categorized_dashboard
        
        # Integrate directly to categorized dashboard
        success = integrate_esg_data_to_categorized_dashboard(
            dashboard_analysis_file=str(dashboard_json),
            company=company,
            year=year
        )
        
        if success:
            print(f"✅ Enhanced dashboard integration completed")
            return True
        else:
            print(f"❌ Enhanced dashboard integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced dashboard integration failed: {e}")
        return False

def run_pdf_summary(analysis_json, output_json):
    """Generate JSON quant summary from comprehensive analysis"""
    # Change output from PDF to JSON
    # output_json = output_pdf.with_suffix('.json') # This line is no longer needed
    
    if os.path.exists(output_json):
        print(f"⏭️ Skipping JSON quant summary, output already exists: {output_json}")
        return output_json
    
    print(f"📋 Generating JSON quant summary...")
    
    try:
        # Simply copy the comprehensive analysis to create the quant summary JSON
        import shutil
        shutil.copy2(analysis_json, output_json)
        print(f"✅ JSON quant summary generated: {output_json}")
        return output_json
        
    except Exception as e:
        print(f"❌ JSON quant summary generation failed: {e}")
        return None

def create_output_directories(company, year):
    """Create organized output directory structure"""
    base_dir = parent_dir / "json" / company / year
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def main():
    parser = argparse.ArgumentParser(description="Enhanced ESG Pipeline - Complete Processing Chain")
    parser.add_argument("--pdf", help="Path to the input PDF file (optional if download enabled)")
    parser.add_argument("--company", required=True, help="Company name (e.g., Amazon, Alibaba)")
    parser.add_argument("--year", required=True, help="Report year (e.g., 2020, 2021, 2022)")
    parser.add_argument("--download", action="store_true", help="Download PDF if not available")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip PDF extraction if JSON exists")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM analysis if JSON exists")
    parser.add_argument("--skip-conversion", action="store_true", help="Skip dashboard conversion if JSON exists")
    parser.add_argument("--skip-integration", action="store_true", help="Skip dashboard integration")
    parser.add_argument("--skip-pdf-summary", action="store_true", help="Skip PDF summary generation")
    
    args = parser.parse_args()
    
    company = args.company
    year = args.year
    
    print(f"\n🚀 Starting Enhanced ESG Pipeline")
    print(f"📋 Company: {company}")
    print(f"📅 Year: {year}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directories
    output_dir = create_output_directories(company, year)
    
    # Define file paths
    if args.pdf:
        pdf_path = args.pdf
    else:
        pdf_path = run_pdf_download(company, year, output_dir)
        if not pdf_path:
            print("❌ No PDF available. Exiting.")
            return
    
    base_name = Path(pdf_path).stem
    structured_json = output_dir / f"{base_name}_structured_content.json"
    analysis_json = output_dir / f"{company.lower()}_{year}_comprehensive_esg_analysis_clean.json"
    dashboard_json = output_dir / f"{company.lower()}_{year}_dashboard_analysis.json"
    summary_json = output_dir / f"{company.lower()}_{year}_quant_summary.json"
    
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📄 PDF: {pdf_path}")
    print(f"📊 Structured JSON: {structured_json}")
    print(f"🤖 Analysis JSON: {analysis_json}")
    print(f"📈 Dashboard JSON: {dashboard_json}")
    print(f"📋 Summary JSON: {summary_json}")
    
    # Step 1: PDF Extraction
    if not args.skip_extraction:
        print(f"\n=== Step 1: PDF Text Extraction ===")
        structured_json = run_pdf_extraction(pdf_path, structured_json, year)
        if not structured_json:
            print("❌ PDF extraction failed. Exiting.")
            return
    else:
        print(f"\n⏭️ Skipping PDF extraction")
    
    # Step 2: LLM Analysis
    if not args.skip_llm:
        print(f"\n=== Step 2: LLM Quantitative Analysis ===")
        analysis_json = run_llm_analysis(structured_json, analysis_json)
        if not analysis_json:
            print("❌ LLM analysis failed. Exiting.")
            return
    else:
        print(f"\n⏭️ Skipping LLM analysis")
    
    # Step 3: Dashboard Conversion
    if not args.skip_conversion:
        print(f"\n=== Step 3: Dashboard Format Conversion ===")
        dashboard_json = run_dashboard_conversion(analysis_json, dashboard_json, company, year)
        if not dashboard_json:
            print("❌ Dashboard conversion failed. Exiting.")
            return
    else:
        print(f"\n⏭️ Skipping dashboard conversion")
    
    # Step 4: Dashboard Integration
    if not args.skip_integration:
        print(f"\n=== Step 4: Dashboard Integration ===")
        success = run_dashboard_integration(dashboard_json, company, year)
        if not success:
            print("❌ Dashboard integration failed.")
    else:
        print(f"\n⏭️ Skipping dashboard integration")
    
    # Step 5: JSON Summary (Optional)
    if not args.skip_pdf_summary:
        print(f"\n=== Step 5: Generate JSON Summary ===")
        summary_json = run_pdf_summary(analysis_json, summary_json)
        if not summary_json:
            print("❌ JSON summary generation failed.")
    else:
        print(f"\n⏭️ Skipping JSON summary generation")
    
    print(f"\n✅ Pipeline completed successfully!")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📊 Generated Files:")
    print(f"   📄 Structured Content: {structured_json}")
    print(f"   🤖 LLM Analysis: {analysis_json}")
    print(f"   📈 Dashboard Data: {dashboard_json}")
    if not args.skip_pdf_summary and summary_json:
        print(f"   📋 Summary JSON: {summary_json}")
    
    print(f"\n🌐 Access your dashboard at: http://localhost:5000")

if __name__ == "__main__":
    main() 