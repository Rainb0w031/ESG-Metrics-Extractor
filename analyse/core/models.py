"""
Pydantic models for ESG analysis.

These models define the structure of analysis inputs and outputs,
ensuring type safety and validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ESGQuantitativeMetrics(BaseModel):
    """
    Pydantic model for ESG quantitative metrics analysis.
    
    Represents a single quantitative metric extracted from an ESG report.
    """
    
    category: str = Field(
        description="ESG category: environmental, social, governance"
    )
    subcategory: str = Field(
        description="Specific subcategory within the ESG category"
    )
    metric_name: str = Field(
        description="Name of the quantitative metric"
    )
    value: str = Field(
        description="Metric value (can be number, percentage, text)"
    )
    unit: str = Field(
        description="Unit of measurement"
    )
    year: str = Field(
        description="Year the metric applies to"
    )
    context: str = Field(
        description="Context and description of the metric"
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0",
        ge=0.0,
        le=1.0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "environmental",
                "subcategory": "carbon_emissions",
                "metric_name": "scope_1_net_emissions_2024",
                "value": "717,096",
                "unit": "tons",
                "year": "2024",
                "context": "Scope 1 net emissions totaled 717,096 tons in 2024",
                "confidence": 0.95
            }
        }


class ESGCategoryResult(BaseModel):
    """
    Result for a single ESG category (Environmental, Social, or Governance).
    
    Contains the comprehensive analysis for one ESG category.
    """
    
    category: str = Field(
        description="Category name: environmental, social, or governance"
    )
    subcategories: Dict[str, Any] = Field(
        default_factory=dict,
        description="Subcategories with details and metrics"
    )
    metrics_count: int = Field(
        default=0,
        description="Total number of metrics extracted"
    )
    details_count: int = Field(
        default=0,
        description="Total number of detail items extracted"
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score for this category"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "environmental",
                "subcategories": {
                    "emissions": {
                        "scope_1": {
                            "details": ["Scope 1 emissions totaled..."],
                            "metrics": {"scope_1_2024": "717,096 tons"}
                        }
                    }
                },
                "metrics_count": 25,
                "details_count": 50,
                "quality_score": 0.92
            }
        }


class ESGAnalysisResult(BaseModel):
    """
    Complete ESG analysis result.
    
    Contains the full analysis output including all three ESG categories
    and metadata about the analysis process.
    """
    
    analysis_type: str = Field(
        description="Type of analysis performed"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Analysis completion timestamp"
    )
    year: str = Field(
        description="Report year"
    )
    
    # Category results (optional based on analysis type)
    environmental: Optional[ESGCategoryResult] = Field(
        default=None,
        description="Environmental analysis results"
    )
    social: Optional[ESGCategoryResult] = Field(
        default=None,
        description="Social analysis results"
    )
    governance: Optional[ESGCategoryResult] = Field(
        default=None,
        description="Governance analysis results"
    )
    
    # Quality metrics
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall analysis quality score"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Analysis metadata (model, config, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_type": "comprehensive",
                "timestamp": "2024-10-08T12:00:00",
                "year": "2024",
                "environmental": {
                    "category": "environmental",
                    "metrics_count": 25,
                    "details_count": 50,
                    "quality_score": 0.92
                },
                "quality_score": 0.90,
                "metadata": {
                    "model_used": "qwen-max",
                    "total_pages": 50,
                    "total_segments": 500
                }
            }
        }


class ESGComprehensiveAnalysis(BaseModel):
    """
    Pydantic model for comprehensive ESG analysis response.
    
    This is the full response structure expected from LLM analysis,
    containing detailed breakdowns for all three ESG categories.
    """
    
    environmental_comprehensive: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comprehensive environmental analysis"
    )
    social_comprehensive: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comprehensive social analysis"
    )
    governance_comprehensive: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comprehensive governance analysis"
    )
    quantitative_metrics: List[ESGQuantitativeMetrics] = Field(
        default_factory=list,
        description="List of quantitative metrics found"
    )
    analysis_summary: str = Field(
        default="",
        description="Overall analysis summary"
    )
    data_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score of the analysis"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "environmental_comprehensive": {
                    "emissions": {
                        "scope_1": {
                            "details": ["Scope 1 emissions..."],
                            "metrics": {"scope_1_2024": "717,096 tons"}
                        }
                    }
                },
                "social_comprehensive": {
                    "diversity_inclusion": {
                        "details": ["Diversity initiatives..."],
                        "metrics": {"diversity_ratio_2024": "45%"}
                    }
                },
                "governance_comprehensive": {
                    "board_governance": {
                        "details": ["Board composition..."],
                        "metrics": {"board_independence_2024": "80%"}
                    }
                },
                "quantitative_metrics": [],
                "analysis_summary": "Comprehensive ESG analysis complete",
                "data_quality_score": 0.92
            }
        }


class ChunkAnalysisResult(BaseModel):
    """Result from analyzing a single chunk of text."""
    
    chunk_number: int = Field(description="Chunk number")
    total_chunks: int = Field(description="Total number of chunks")
    content: Dict[str, Any] = Field(
        default_factory=dict,
        description="Analyzed content"
    )
    processing_time: float = Field(
        default=0.0,
        description="Processing time in seconds"
    )
    success: bool = Field(
        default=True,
        description="Whether processing was successful"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if processing failed"
    )

