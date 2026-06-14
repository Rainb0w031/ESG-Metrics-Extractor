"""Quick test of PDF extraction (no LLM)."""
from extract.pipeline import PDFExtractor, ExtractorConfig
from pathlib import Path

pdf_path = Path('input/amazon_2022.pdf')
output_path = Path('output/amazon_2022_extraction_test.json')
output_path.parent.mkdir(exist_ok=True)

config = ExtractorConfig(use_llm=False, enable_esg_analysis=True)
extractor = PDFExtractor(config)

print(f'Extracting: {pdf_path}')
result = extractor.extract(pdf_path, output_path)
print(f'Pages processed: {len(result.get("pages", []))}')
print(f'Output saved to: {output_path}')
