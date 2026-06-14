# Reports Core Scripts Reference Compilation

This directory contains a reference compilation of all core scripts from the reports-indexing-main project, organized by functionality for easy reference during the modularization process.

## Directory Structure

```
reports-core-scripts-reference/
├── 01-pdf-extraction/
│   ├── pdf_content_extractor_ultra_robust.py          # Core PDF extraction engine
│   └── enhanced_structured_content_producer.py        # High-level PDF processing orchestrator
├── 02-llm-analysis/
│   └── quantitative_llm_analysis_clean_fixed.py       # LLM-based ESG quantitative analysis
├── 03-dashboard-conversion/
│   └── convert_comprehensive_to_dashboard_enhanced.py # Dashboard format conversion with metric enhancement
├── 04-pipeline-orchestration/
│   └── run_full_pipeline.py                          # Complete pipeline orchestrator
├── 05-supporting-utilities/
│   ├── direct_api_client.py                          # LLM API client wrapper
│   ├── integrate_esg_data_to_categorized_dashboard.py # Dashboard integration utility
│   └── config.py                                     # Configuration management
└── README.md                                         # This file
```

## Script Dependencies and Relationships

### Core Processing Flow

1. **PDF Extraction** (`01-pdf-extraction/`)
   - `pdf_content_extractor_ultra_robust.py` - Core extraction engine
   - `enhanced_structured_content_producer.py` - Uses the core extractor and adds error detection/fixing

2. **LLM Analysis** (`02-llm-analysis/`)
   - `quantitative_llm_analysis_clean_fixed.py` - Processes structured content from step 1
   - Depends on `direct_api_client.py` for LLM interactions

3. **Dashboard Conversion** (`03-dashboard-conversion/`)
   - `convert_comprehensive_to_dashboard_enhanced.py` - Converts LLM analysis to dashboard format
   - Uses metric enhancement and categorization

4. **Pipeline Orchestration** (`04-pipeline-orchestration/`)
   - `run_full_pipeline.py` - Orchestrates all steps
   - Coordinates between all modules

5. **Supporting Utilities** (`05-supporting-utilities/`)
   - `direct_api_client.py` - LLM API client used by analysis module
   - `integrate_esg_data_to_categorized_dashboard.py` - Dashboard integration
   - `config.py` - Configuration management

## Key Integration Points for Prompter Project

### 1. PDF Extraction Module
- **Current**: Uses custom PDF extraction with error handling
- **Prompter Integration**: Should inherit from `BasePromptModel` and use prompter's text chunking middleware
- **Dependencies**: `pdf_content_extractor_ultra_robust.py` (core engine)

### 2. LLM Analysis Module
- **Current**: Uses `direct_api_client.py` for LLM interactions
- **Prompter Integration**: Should use prompter's `BaseChat` and structured output capabilities
- **Dependencies**: `direct_api_client.py` (to be replaced with prompter's client)

### 3. Dashboard Conversion Module
- **Current**: Standalone conversion with metric enhancement
- **Prompter Integration**: Should use prompter's data models and I/O utilities
- **Dependencies**: None (self-contained)

### 4. Pipeline Orchestration
- **Current**: Coordinates all modules with subprocess calls
- **Prompter Integration**: Should compose prompter-based modules directly
- **Dependencies**: All other modules

## Modularization Strategy

### Phase 1: Create ESG Base Classes
- Create `ESGBasePromptModel` extending `BasePromptModel`
- Create ESG-specific data models in `prompter/esg/models.py`

### Phase 2: Modularize Core Scripts
- `ESGPDFExtractor` (extends `ESGBasePromptModel`)
- `ESGQuantitativeAnalyzer` (extends `ESGBasePromptModel`)
- `ESGDashboardConverter` (extends `ESGBasePromptModel`)
- `ESGPipeline` (composes other modules)

### Phase 3: Integration Points
- Use prompter's template system for ESG prompts
- Integrate with prompter's middleware for text processing
- Use prompter's configuration management
- Leverage prompter's logging and I/O utilities

## File Descriptions

### 01-pdf-extraction/
- **pdf_content_extractor_ultra_robust.py**: Core PDF text extraction with robust error handling
- **enhanced_structured_content_producer.py**: High-level orchestrator that uses the core extractor

### 02-llm-analysis/
- **quantitative_llm_analysis_clean_fixed.py**: LLM-based ESG quantitative analysis with chunking

### 03-dashboard-conversion/
- **convert_comprehensive_to_dashboard_enhanced.py**: Converts analysis to dashboard format with metric enhancement

### 04-pipeline-orchestration/
- **run_full_pipeline.py**: Complete pipeline that orchestrates all steps

### 05-supporting-utilities/
- **direct_api_client.py**: LLM API client wrapper
- **integrate_esg_data_to_categorized_dashboard.py**: Dashboard integration utility
- **config.py**: Configuration management

## Notes for Modularization

1. **Dependency Management**: Current scripts have tight coupling - modularization should create clean interfaces
2. **Error Handling**: Current scripts have robust error handling - should integrate with prompter's logging
3. **Configuration**: Current scripts use hardcoded settings - should use prompter's configuration system
4. **Testing**: Current scripts lack comprehensive testing - should add tests using prompter's test framework

This reference compilation serves as the foundation for creating fully modularized, prompter-integrated ESG processing capabilities. 