"""
Dashboard Converter - Main orchestrator for ESG dashboard conversion.

Coordinates the full pipeline:
1. Load comprehensive analysis
2. Extract metrics
3. LLM-enhance (names, categories, importance)
4. Clean values
5. Validate metrics
6. Save dashboard format
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig
from ..core.config import ConversionConfig
from ..core.models import DashboardData
from ..extraction import MetricExtractor
from ..cleaning.value_cleaner import ValueCleaner
from ..validation.validators import MetricValidator
from ..enhancement.combined_processor import CombinedProcessor, ProcessingConfig


@dataclass
class ConversionResult:
    """Result of dashboard conversion."""
    success: bool
    output_file: Optional[str] = None
    metrics_count: int = 0
    validation_issues: int = 0
    error: Optional[str] = None


class DashboardConverter:
    """
    Main orchestrator for comprehensive ESG to dashboard conversion.
    
    Features:
    - Full pipeline coordination
    - LLM-enhanced metric processing
    - Parallel batch processing
    - Validation and quality checks
    - Progress tracking
    """
    
    def __init__(self, config: Optional[ConversionConfig] = None):
        """
        Initialize the converter.
        
        Args:
            config: Optional conversion configuration
        """
        self.config = config or ConversionConfig()
        
        # Initialize API client
        self.client = DirectAPIClient(self.config.api_config)
        
        # Initialize components
        self.extractor = MetricExtractor()
        self.cleaner = ValueCleaner()
        self.validator = MetricValidator()
        self.processor = CombinedProcessor(
            api_client=self.client,
            config=ProcessingConfig(
                batch_size=self.config.batch_size,
                max_workers=self.config.max_workers
            )
        )
    
    def convert(self,
                input_file: str,
                output_file: str,
                company: str = "Unknown",
                year: str = "Unknown") -> ConversionResult:
        """
        Convert comprehensive ESG analysis to dashboard format.
        
        Args:
            input_file: Path to comprehensive ESG analysis JSON
            output_file: Path to output dashboard JSON
            company: Company name
            year: Report year
            
        Returns:
            ConversionResult with success status and details
        """
        logger.info(f"Converting {input_file} to dashboard format...")
        logger.info(f"Company: {company}, Year: {year}")
        
        # Step 1: Load input
        try:
            analysis_data = self._load_input(input_file)
        except Exception as e:
            logger.error(f"Failed to load input: {e}")
            return ConversionResult(success=False, error=str(e))
        
        # Step 2: Extract metrics
        logger.info("Step 1: Extracting metrics from analysis...")
        metrics = self.extractor.extract(analysis_data, company, year)
        
        if not metrics:
            logger.error("No metrics extracted from analysis")
            return ConversionResult(success=False, error="No metrics found")
        
        logger.info(f"Extracted {len(metrics)} metrics")
        
        # Step 3: LLM enhancement (combined processing)
        if self.config.enhance_names or self.config.generate_categories or self.config.analyze_importance:
            logger.info("Step 2: Combined LLM processing (names, categories, importance)...")
            metrics = self.processor.process_all(metrics, company, year)
        
        # Step 4: Clean values
        if self.config.clean_values:
            logger.info("Step 3: Cleaning metric values...")
            metrics = self.cleaner.clean_metrics(metrics)
        
        # Step 5: Validate metrics
        validation_issues = []
        if self.config.validate_metrics:
            logger.info("Step 4: Validating metrics...")
            metrics, validation_issues = self.validator.validate_metrics(metrics)
        
        # Step 6: Create dashboard data
        dashboard = DashboardData(
            company=company,
            year=year,
            file_path=str(input_file),
            metrics=metrics
        )
        
        # Add validation summary if issues found
        if validation_issues:
            dashboard.validation_summary = {
                'total_issues': len(validation_issues),
                'critical_issues': sum(1 for i in validation_issues if i.get('severity') == 'critical'),
                'high_priority_issues': sum(1 for i in validation_issues if i.get('severity') == 'high'),
                'issues': validation_issues
            }
        
        # Step 7: Save output
        try:
            self._save_output(dashboard, output_file)
            logger.info(f"Dashboard saved to: {output_file}")
            logger.info(f"Final metrics count: {len(metrics)}")
            
            return ConversionResult(
                success=True,
                output_file=output_file,
                metrics_count=len(metrics),
                validation_issues=len(validation_issues)
            )
            
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            return ConversionResult(success=False, error=str(e))
    
    def _load_input(self, input_file: str) -> Dict[str, Any]:
        """Load input JSON file."""
        path = Path(input_file)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_output(self, dashboard: DashboardData, output_file: str):
        """Save dashboard data to JSON file."""
        path = Path(output_file)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dashboard.to_dict(), f, indent=2, ensure_ascii=False)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert comprehensive ESG analysis to dashboard format"
    )
    parser.add_argument("input_file", help="Path to comprehensive ESG analysis JSON")
    parser.add_argument("output_file", help="Path to output dashboard JSON")
    parser.add_argument("--company", default="Unknown", help="Company name")
    parser.add_argument("--year", default="Unknown", help="Report year")
    parser.add_argument("--batch-size", type=int, default=15, help="Batch size for LLM processing")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers")
    parser.add_argument("--no-enhance", action="store_true", help="Skip LLM enhancement")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    
    args = parser.parse_args()
    
    # Create config
    config = ConversionConfig(
        batch_size=args.batch_size,
        max_workers=args.workers,
        enhance_names=not args.no_enhance,
        generate_categories=not args.no_enhance,
        analyze_importance=not args.no_enhance,
        validate_metrics=not args.no_validate
    )
    
    # Run conversion
    converter = DashboardConverter(config)
    result = converter.convert(
        input_file=args.input_file,
        output_file=args.output_file,
        company=args.company,
        year=args.year
    )
    
    if result.success:
        print(f"\n[OK] Conversion completed successfully!")
        print(f"Output: {result.output_file}")
        print(f"Metrics: {result.metrics_count}")
        if result.validation_issues > 0:
            print(f"Validation issues: {result.validation_issues}")
    else:
        print(f"\n[ERROR] Conversion failed: {result.error}")
        exit(1)


if __name__ == "__main__":
    main()
