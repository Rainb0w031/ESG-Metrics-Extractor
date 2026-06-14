"""
ESG Metrics Pipeline - End-to-End Runner

Chains all 4 modularized steps together:
1. PDF Extraction (extract/) - Extract text from PDF reports
2. LLM ESG Analysis (analyse/) - Analyze text for ESG content
3. Dashboard Conversion (convert/) - Convert analysis to dashboard format
4. Dashboard Integration (integrate/) - Integrate into categorized dashboard

Usage:
    python run_pipeline.py report.pdf --company "Company Name" --year 2024
    python run_pipeline.py report.pdf --company "Amazon" --year 2022 --output-dir ./output
    python run_pipeline.py report.pdf --skip-integration  # Stop after conversion
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from loguru import logger


@dataclass
class PipelineConfig:
    """Configuration for the full pipeline."""
    # Input/Output
    output_dir: Path = field(default_factory=lambda: Path("output"))
    
    # Step control
    skip_extraction: bool = False  # Start from existing extraction
    skip_analysis: bool = False    # Start from existing analysis
    skip_conversion: bool = False  # Start from existing conversion
    skip_integration: bool = False # Stop after conversion
    
    # Extraction settings
    use_llm_extraction: bool = True
    enable_esg_analysis: bool = True
    
    # Analysis settings
    analysis_type: str = "comprehensive"
    
    # Conversion settings
    batch_size: int = 15
    max_workers: int = 3
    enhance_names: bool = True
    
    # Integration settings
    categorized_dashboard_path: str = "dashboard/llm_enhanced_esg_data_categorized.json"
    clean_duplicates: bool = True
    
    def __post_init__(self):
        self.output_dir = Path(self.output_dir)


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    success: bool
    company: str
    year: str
    steps_completed: List[str] = field(default_factory=list)
    output_files: Dict[str, str] = field(default_factory=dict)
    metrics_count: int = 0
    elapsed_seconds: float = 0.0
    error: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success:
            return (
                f"Pipeline completed successfully for {self.company} {self.year}\n"
                f"  Steps: {' -> '.join(self.steps_completed)}\n"
                f"  Metrics: {self.metrics_count}\n"
                f"  Time: {self.elapsed_seconds:.1f}s"
            )
        return f"Pipeline failed: {self.error}"


class ESGPipeline:
    """
    End-to-end ESG analysis pipeline.
    
    Orchestrates all 4 modularized steps:
    1. extract/ - PDF text extraction
    2. analyse/ - LLM ESG analysis
    3. convert/ - Dashboard conversion
    4. integrate/ - Dashboard integration
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the pipeline."""
        self.config = config or PipelineConfig()
        self._setup_logging()
        self._ensure_output_dir()
    
    def _setup_logging(self):
        """Configure logging."""
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
            level="INFO"
        )
        
        # Also log to file
        log_file = self.config.output_dir / "pipeline.log"
        logger.add(log_file, rotation="10 MB", level="DEBUG")
    
    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self,
            pdf_path: str,
            company: str = "Unknown",
            year: str = "Unknown",
            extraction_file: str = None,
            analysis_file: str = None,
            dashboard_file: str = None) -> PipelineResult:
        """
        Run the full ESG analysis pipeline.
        
        Args:
            pdf_path: Path to input PDF file
            company: Company name
            year: Report year
            extraction_file: Optional pre-existing extraction file (skip step 1)
            analysis_file: Optional pre-existing analysis file (skip steps 1-2)
            dashboard_file: Optional pre-existing dashboard file (skip steps 1-3)
            
        Returns:
            PipelineResult with success status and details
        """
        start_time = time.time()
        steps_completed = []
        output_files = {}
        
        logger.info("=" * 60)
        logger.info(f"ESG PIPELINE - {company} {year}")
        logger.info("=" * 60)
        
        # Generate output file paths
        base_name = f"{company.lower().replace(' ', '_')}_{year}"
        extraction_output = self.config.output_dir / f"{base_name}_extraction.json"
        analysis_output = self.config.output_dir / f"{base_name}_analysis.json"
        dashboard_output = self.config.output_dir / f"{base_name}_dashboard.json"
        
        try:
            # ============================================================
            # STEP 1: PDF Extraction
            # ============================================================
            if extraction_file:
                logger.info("[STEP 1] Using provided extraction file")
                extraction_output = Path(extraction_file)
            elif not self.config.skip_extraction:
                logger.info("[STEP 1] PDF Extraction")
                logger.info("-" * 40)
                
                extraction_result = self._run_extraction(pdf_path, extraction_output)
                
                if not extraction_result.get('success', True):
                    raise RuntimeError(f"Extraction failed: {extraction_result.get('error')}")
                
                steps_completed.append("extraction")
                output_files['extraction'] = str(extraction_output)
                logger.info(f"[OK] Extraction complete: {extraction_output}")
            
            # ============================================================
            # STEP 2: LLM ESG Analysis
            # ============================================================
            if analysis_file:
                logger.info("[STEP 2] Using provided analysis file")
                analysis_output = Path(analysis_file)
            elif not self.config.skip_analysis:
                logger.info("\n[STEP 2] LLM ESG Analysis")
                logger.info("-" * 40)
                
                analysis_result = self._run_analysis(extraction_output, analysis_output)
                
                steps_completed.append("analysis")
                output_files['analysis'] = str(analysis_output)
                logger.info(f"[OK] Analysis complete: {analysis_output}")
            
            # ============================================================
            # STEP 3: Dashboard Conversion
            # ============================================================
            if dashboard_file:
                logger.info("[STEP 3] Using provided dashboard file")
                dashboard_output = Path(dashboard_file)
            elif not self.config.skip_conversion:
                logger.info("\n[STEP 3] Dashboard Conversion")
                logger.info("-" * 40)
                
                conversion_result = self._run_conversion(
                    analysis_output, dashboard_output, company, year
                )
                
                if not conversion_result.success:
                    raise RuntimeError(f"Conversion failed: {conversion_result.error}")
                
                steps_completed.append("conversion")
                output_files['dashboard'] = str(dashboard_output)
                metrics_count = conversion_result.metrics_count
                logger.info(f"[OK] Conversion complete: {dashboard_output}")
            else:
                metrics_count = 0
            
            # ============================================================
            # STEP 4: Dashboard Integration
            # ============================================================
            if not self.config.skip_integration:
                logger.info("\n[STEP 4] Dashboard Integration")
                logger.info("-" * 40)
                
                integration_result = self._run_integration(
                    dashboard_output, company, year
                )
                
                if not integration_result.success:
                    raise RuntimeError(f"Integration failed: {integration_result.message}")
                
                steps_completed.append("integration")
                output_files['categorized'] = self.config.categorized_dashboard_path
                metrics_count = integration_result.metrics_added
                logger.info(f"[OK] Integration complete")
            
            # Success
            elapsed = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info(f"PIPELINE COMPLETE - {elapsed:.1f}s")
            logger.info("=" * 60)
            
            return PipelineResult(
                success=True,
                company=company,
                year=year,
                steps_completed=steps_completed,
                output_files=output_files,
                metrics_count=metrics_count,
                elapsed_seconds=elapsed
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Pipeline failed: {e}")
            
            return PipelineResult(
                success=False,
                company=company,
                year=year,
                steps_completed=steps_completed,
                output_files=output_files,
                elapsed_seconds=elapsed,
                error=str(e)
            )
    
    def _run_extraction(self, pdf_path: str, output_path: Path) -> Dict[str, Any]:
        """Run PDF extraction step."""
        from extract.pipeline import LLMPDFExtractor, PDFExtractor, ExtractorConfig
        from extract.api import APIConfig
        
        config = ExtractorConfig(
            use_llm=self.config.use_llm_extraction,
            enable_esg_analysis=self.config.enable_esg_analysis,
            api_config=APIConfig.from_env() if self.config.use_llm_extraction else None
        )
        
        if self.config.use_llm_extraction:
            extractor = LLMPDFExtractor(config)
        else:
            extractor = PDFExtractor(config)
        
        return extractor.extract(Path(pdf_path), output_path)
    
    def _run_analysis(self, extraction_file: Path, output_path: Path) -> Dict[str, Any]:
        """Run LLM ESG analysis step using direct API calls."""
        from analyse.processors.direct_processor import DirectAnalyzer, DirectProcessorConfig
        from analyse.prompts.simple_prompt import SimplePromptBuilder
        from analyse.merging.esg_merger import ESGMerger
        from extract.api import APIConfig
        
        # Load extraction data
        with open(extraction_file, 'r', encoding='utf-8') as f:
            extraction_data = json.load(f)
        
        # Extract text segments
        text_segments = []
        for page in extraction_data.get('pages', []):
            for segment in page.get('text_segments', []):
                if isinstance(segment, dict):
                    text = segment.get('text', '')
                else:
                    text = str(segment)
                if text and text.strip():
                    text_segments.append(text.strip())
        
        logger.info(f"Extracted {len(text_segments)} text segments for analysis")
        
        if not text_segments:
            logger.warning("No text segments found")
            return {"analysis_metadata": {"status": "no_content"}}
        
        # Chunk text (larger chunks since prompt is simpler)
        chunk_size = 80  # segments per chunk (can be larger with simpler prompt)
        chunks = [text_segments[i:i+chunk_size] for i in range(0, len(text_segments), chunk_size)]
        logger.info(f"Created {len(chunks)} chunks for analysis")
        
        # Build prompts using simplified prompt builder
        prompt_builder = SimplePromptBuilder()
        year = extraction_data.get('metadata', {}).get('year', '2022')
        
        prompts = []
        for i, chunk in enumerate(chunks):
            chunk_text = '\n'.join(chunk)
            prompt = prompt_builder.build(chunk_text, i + 1, len(chunks), year)
            prompts.append(prompt)
        
        # Initialize analyzer with direct API
        config = DirectProcessorConfig(api_config=APIConfig.from_env())
        analyzer = DirectAnalyzer(config)
        merger = ESGMerger()
        
        # Process with direct API calls
        logger.info("Processing with direct API calls...")
        result = analyzer.analyze_with_prompts(
            prompts=prompts,
            analysis_type="comprehensive",
            merge_func=merger.merge,
            parallel=True,
            max_workers=self.config.max_workers
        )
        
        # Add metadata
        result['analysis_metadata'] = {
            'total_segments': len(text_segments),
            'total_chunks': len(chunks),
            'analysis_type': self.config.analysis_type,
            'status': 'completed'
        }
        
        # Save result
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return result
    
    def _run_conversion(self, 
                        analysis_file: Path, 
                        output_path: Path,
                        company: str,
                        year: str):
        """Run dashboard conversion step."""
        from convert.pipeline import DashboardConverter
        from convert.core.config import ConversionConfig
        from extract.api import APIConfig
        
        config = ConversionConfig(
            api_config=APIConfig.from_env(),
            batch_size=self.config.batch_size,
            max_workers=self.config.max_workers,
            enhance_names=self.config.enhance_names
        )
        
        converter = DashboardConverter(config)
        return converter.convert(
            input_file=str(analysis_file),
            output_file=str(output_path),
            company=company,
            year=year
        )
    
    def _run_integration(self, dashboard_file: Path, company: str, year: str):
        """Run dashboard integration step."""
        from integrate.pipeline import DashboardIntegrator
        from integrate.core.config import IntegrationConfig
        
        config = IntegrationConfig(
            categorized_dashboard_path=self.config.categorized_dashboard_path,
            clean_duplicates=self.config.clean_duplicates
        )
        
        integrator = DashboardIntegrator(config)
        return integrator.integrate(
            dashboard_file=str(dashboard_file),
            company=company,
            year=year
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ESG Metrics Pipeline - End-to-End Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline from PDF
  python run_pipeline.py report.pdf --company "Amazon" --year 2022
  
  # Skip to analysis (use existing extraction)
  python run_pipeline.py report.pdf --company "Amazon" --year 2022 \\
      --extraction-file output/amazon_2022_extraction.json
  
  # Skip to conversion (use existing analysis)
  python run_pipeline.py report.pdf --company "Amazon" --year 2022 \\
      --analysis-file output/amazon_2022_analysis.json
  
  # Stop after conversion (no integration)
  python run_pipeline.py report.pdf --company "Amazon" --year 2022 --skip-integration
  
  # Custom output directory
  python run_pipeline.py report.pdf --company "Amazon" --year 2022 --output-dir ./results
        """
    )
    
    # Required arguments
    parser.add_argument("pdf_path", help="Path to PDF report file")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--year", required=True, help="Report year")
    
    # Output options
    parser.add_argument("--output-dir", default="output", 
                       help="Output directory (default: output)")
    
    # Skip options
    parser.add_argument("--skip-extraction", action="store_true",
                       help="Skip extraction step")
    parser.add_argument("--skip-analysis", action="store_true",
                       help="Skip analysis step")
    parser.add_argument("--skip-conversion", action="store_true",
                       help="Skip conversion step")
    parser.add_argument("--skip-integration", action="store_true",
                       help="Skip integration step (stop after conversion)")
    
    # Input file overrides (resume from intermediate step)
    parser.add_argument("--extraction-file", 
                       help="Use existing extraction file (skip step 1)")
    parser.add_argument("--analysis-file",
                       help="Use existing analysis file (skip steps 1-2)")
    parser.add_argument("--dashboard-file",
                       help="Use existing dashboard file (skip steps 1-3)")
    
    # Processing options
    parser.add_argument("--no-llm-extraction", action="store_true",
                       help="Use rule-based extraction (no LLM)")
    parser.add_argument("--batch-size", type=int, default=15,
                       help="Batch size for LLM processing (default: 15)")
    parser.add_argument("--workers", type=int, default=3,
                       help="Parallel workers for LLM processing (default: 3)")
    parser.add_argument("--no-enhance", action="store_true",
                       help="Skip LLM enhancement in conversion")
    
    # Integration options
    parser.add_argument("--categorized-dashboard",
                       default="dashboard/llm_enhanced_esg_data_categorized.json",
                       help="Path to categorized dashboard file")
    parser.add_argument("--no-duplicate-cleaning", action="store_true",
                       help="Skip duplicate cleaning during integration")
    
    args = parser.parse_args()
    
    # Create config
    config = PipelineConfig(
        output_dir=Path(args.output_dir),
        skip_extraction=args.skip_extraction,
        skip_analysis=args.skip_analysis,
        skip_conversion=args.skip_conversion,
        skip_integration=args.skip_integration,
        use_llm_extraction=not args.no_llm_extraction,
        batch_size=args.batch_size,
        max_workers=args.workers,
        enhance_names=not args.no_enhance,
        categorized_dashboard_path=args.categorized_dashboard,
        clean_duplicates=not args.no_duplicate_cleaning
    )
    
    # Run pipeline
    pipeline = ESGPipeline(config)
    result = pipeline.run(
        pdf_path=args.pdf_path,
        company=args.company,
        year=args.year,
        extraction_file=args.extraction_file,
        analysis_file=args.analysis_file,
        dashboard_file=args.dashboard_file
    )
    
    # Print result
    print("\n" + "=" * 60)
    print(result)
    print("=" * 60)
    
    if result.success:
        print("\nOutput files:")
        for step, path in result.output_files.items():
            print(f"  {step}: {path}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
