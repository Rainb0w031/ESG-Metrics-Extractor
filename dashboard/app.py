#!/usr/bin/env python3
"""
ESG Dashboard - Data Exploration, Visualization, and Benchmarking
"""

from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import re

# Import the dynamic comparison analyzer
from dynamic_comparison_analyzer import comparison_analyzer

app = Flask(__name__)

# Global data storage
esg_data = {}
companies = []

def load_esg_data():
    """Load ESG data from the categorized JSON file"""
    global esg_data, companies
    
    print("🔄 Loading ESG data...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Clear existing data
    esg_data = {}
    companies = []
    
    # Use absolute path to the categorized data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    categorized_file = os.path.join(current_dir, "llm_enhanced_esg_data_categorized.json")
    print(f"Looking for categorized file: {categorized_file}")
    print(f"File exists: {os.path.exists(categorized_file)}")
    
    if os.path.exists(categorized_file):
        try:
            with open(categorized_file, 'r', encoding='utf-8') as f:
                categorized_data = json.load(f)
            
            print(f"✅ Successfully loaded categorized data with {len(categorized_data)} entries")
            
            # Process categorized data structure
            for key, data in categorized_data.items():
                company_name = data.get('company', '')
                year = data.get('year', '')
                
                if company_name not in companies:
                    companies.append(company_name)
                
                # Store the data with metrics directly accessible - this is the correct structure
                esg_data[key] = {
                    'company': company_name,
                    'year': year,
                    'data': data,  # Store the entire data object, not just metrics
                    'file_path': data.get('file_path', '')
                }
            
            print(f"✅ Loaded LLM enhanced categorized data: {len(categorized_data)} datasets")
            print(f"📊 Companies: {companies}")
            print(f"📊 Global esg_data keys: {list(esg_data.keys())}")
            return
        except Exception as e:
            print(f"❌ Error loading LLM enhanced categorized data: {e}")
            import traceback
            traceback.print_exc()
            return
    
    print("❌ Categorized file not found, trying other options...")
    
    # Try to load LLM enhanced data
    enhanced_file = os.path.join(current_dir, "llm_enhanced_esg_data.json")
    print(f"Looking for enhanced file: {enhanced_file}")
    print(f"File exists: {os.path.exists(enhanced_file)}")
    
    if os.path.exists(enhanced_file):
        try:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)
            
            # Convert enhanced data to dashboard format
            for key, data in enhanced_data.items():
                company_name = data.get('company', '')
                year = data.get('year', '')
                
                if company_name not in companies:
                    companies.append(company_name)
                
                esg_data[key] = {
                    'company': company_name,
                    'year': year,
                    'data': data,
                    'file_path': data.get('file_path', '')
                }
            
            print(f"✅ Loaded LLM enhanced data: {len(enhanced_data)} datasets")
            print(f"📊 Companies: {companies}")
            return
        except Exception as e:
            print(f"❌ Error loading LLM enhanced data: {e}")
    
    # Fallback to original enhanced data
    enhanced_file = os.path.join(current_dir, "enhanced_esg_data.json")
    print(f"Looking for original enhanced file: {enhanced_file}")
    print(f"File exists: {os.path.exists(enhanced_file)}")
    
    if os.path.exists(enhanced_file):
        try:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)
            
            # Convert enhanced data to dashboard format
            for key, data in enhanced_data.items():
                company_name = data.get('company', '')
                year = data.get('year', '')
                
                if company_name not in companies:
                    companies.append(company_name)
                
                esg_data[key] = {
                    'company': company_name,
                    'year': year,
                    'data': data,
                    'file_path': data.get('file_path', '')
                }
            
            print(f"✅ Loaded original enhanced data: {len(enhanced_data)} datasets")
            print(f"📊 Companies: {companies}")
            return
        except Exception as e:
            print(f"❌ Error loading original enhanced data: {e}")
    
    # Fallback to Excel-converted data
    excel_file = os.path.join(current_dir, "esg_data.json")
    print(f"Looking for Excel file: {excel_file}")
    print(f"File exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        try:
            with open(excel_file, 'r', encoding='utf-8') as f:
                excel_data = json.load(f)
            
            # Convert Excel data to dashboard format
            for key, data in excel_data.items():
                company_name = data.get('company', '')
                year = data.get('year', '')
                
                if company_name not in companies:
                    companies.append(company_name)
                
                esg_data[key] = {
                    'company': company_name,
                    'year': year,
                    'data': data,
                    'file_path': data.get('file_path', '')
                }
            
            print(f"✅ Loaded Excel-converted data: {len(excel_data)} datasets")
            print(f"📊 Companies: {companies}")
            return
        except Exception as e:
            print(f"❌ Error loading Excel-converted data: {e}")
    
    print("No enhanced data found.")
    print("✅ Loaded Excel-converted data: 0 datasets")
    print("📊 Total metrics: 0")
    print("📊 Companies: []")

def extract_metrics_from_json(data):
    """Extract metrics from processed ESG data structure with LLM enhancements"""
    metrics = []
    
    # Handle the categorized data structure (direct metrics array)
    if isinstance(data, dict) and 'metrics' in data:
        print(f"📊 Found {len(data['metrics'])} metrics in direct metrics array")
        for metric in data['metrics']:
            enhanced_metric = {
                'metric_name': metric.get('metric_name', ''),
                'value': metric.get('value', ''),
                'description': metric.get('enhanced_description', metric.get('description', '')),
                'category': metric.get('category', ''),
                'type': metric.get('type', ''),
                'company': metric.get('company', ''),
                'year': metric.get('year', ''),
                'original_key': metric.get('original_key', ''),
                'original_value': metric.get('original_value', ''),
                'unit': metric.get('formatted_unit', metric.get('unit', '')),
                'area': metric.get('esg_area', metric.get('area', '')),
                'subcategory': metric.get('subcategory', ''),
                'notes': metric.get('notes', ''),
                'actions': f"View details for {metric.get('metric_name', '')}",
                # LLM enhanced fields
                'significance': metric.get('significance', ''),
                'industry_context': metric.get('industry_context', ''),
                'interpretation': metric.get('interpretation', ''),
                'recommendations': metric.get('recommendations', ''),
                'data_quality': metric.get('data_quality', ''),
                'cleaned_value': metric.get('cleaned_value', ''),
                'value_interpretation': metric.get('value_interpretation', ''),
                'comparison_context': metric.get('comparison_context', ''),
                'metric_type': metric.get('metric_type', ''),
                'importance': metric.get('importance', ''),
                'reporting_standard': metric.get('reporting_standard', '')
            }
            metrics.append(enhanced_metric)
        return metrics
    
    # Handle the enhanced data structure (nested metrics)
    if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict) and 'metrics' in data['data']:
        print(f"📊 Found {len(data['data']['metrics'])} metrics in nested data structure")
        for metric in data['data']['metrics']:
            enhanced_metric = {
                'metric_name': metric.get('metric_name', ''),
                'value': metric.get('value', ''),
                'description': metric.get('enhanced_description', metric.get('description', '')),
                'category': metric.get('category', ''),
                'type': metric.get('type', ''),
                'company': metric.get('company', ''),
                'year': metric.get('year', ''),
                'original_key': metric.get('original_key', ''),
                'original_value': metric.get('original_value', ''),
                'unit': metric.get('formatted_unit', metric.get('unit', '')),
                'area': metric.get('esg_area', metric.get('area', '')),
                'subcategory': metric.get('subcategory', ''),
                'notes': metric.get('notes', ''),
                'actions': f"View details for {metric.get('metric_name', '')}",
                # LLM enhanced fields
                'significance': metric.get('significance', ''),
                'industry_context': metric.get('industry_context', ''),
                'interpretation': metric.get('interpretation', ''),
                'recommendations': metric.get('recommendations', ''),
                'data_quality': metric.get('data_quality', ''),
                'cleaned_value': metric.get('cleaned_value', ''),
                'value_interpretation': metric.get('value_interpretation', ''),
                'comparison_context': metric.get('comparison_context', ''),
                'metric_type': metric.get('metric_type', ''),
                'importance': metric.get('importance', ''),
                'reporting_standard': metric.get('reporting_standard', '')
            }
            metrics.append(enhanced_metric)
        return metrics
    
    # Handle legacy data structure
    if isinstance(data, dict):
        print(f"📊 Processing legacy data structure with {len(data)} keys")
        for key, value in data.items():
            if isinstance(value, dict):
                metrics.append({
                    'metric_name': key,
                    'value': str(value.get('value', '')),
                    'description': str(value.get('description', '')),
                    'category': str(value.get('category', '')),
                    'type': str(value.get('type', '')),
                    'company': str(value.get('company', '')),
                    'year': str(value.get('year', '')),
                    'original_key': key,
                    'original_value': str(value.get('original_value', '')),
                    'unit': str(value.get('unit', '')),
                    'area': str(value.get('area', '')),
                    'subcategory': str(value.get('subcategory', '')),
                    'notes': str(value.get('notes', '')),
                    'actions': f"View details for {key}"
                })
    
    print(f"📊 Total metrics extracted: {len(metrics)}")
    return metrics

def create_visualizations(company_data):
    """Create comprehensive visualizations for ESG data using strictly loaded metrics"""
    viz_data = {}
    
    try:
        print(f"🔄 Creating visualizations for {len(company_data)} companies...")
        
        # Extract all metrics from the loaded data
        all_metrics = []
        for key, data in company_data.items():
            print(f"📊 Processing {key}: {data.get('company', 'Unknown')} {data.get('year', 'Unknown')}")
            print(f"   Data structure keys: {list(data.keys())}")
            
            # Extract metrics using the same method as exploration page
            metrics = extract_metrics_from_json(data['data'])
            print(f"   Found {len(metrics)} metrics")
            
            # Debug: Show first few metrics
            if metrics:
                print(f"   Sample metrics: {[m.get('metric_name', 'N/A') for m in metrics[:3]]}")
                print(f"   Sample areas: {[m.get('area', 'N/A') for m in metrics[:3]]}")
                print(f"   Sample categories: {[m.get('category', 'N/A') for m in metrics[:3]]}")
            
            for metric in metrics:
                # Ensure company and year are set correctly
                metric['company'] = data.get('company', 'Unknown')
                metric['year'] = data.get('year', 'Unknown')
                all_metrics.append(metric)
        
        print(f"📊 Total metrics extracted: {len(all_metrics)}")
        
        if not all_metrics:
            print("⚠️ No metrics found for visualization")
            return viz_data
        
        # Create DataFrame from the actual metrics
        df = pd.DataFrame(all_metrics)
        print(f"📊 DataFrame created with {len(df)} rows and columns: {list(df.columns)}")
        
        # Debug: Show actual data counts
        print(f"📊 Companies in data: {df['company'].unique()}")
        print(f"📊 Years in data: {df['year'].unique()}")
        print(f"📊 Areas in data: {df['area'].unique()}")
        print(f"📊 Categories in data: {df['category'].unique()}")
        
        # Debug: Show sample data
        print(f"📊 Sample area values: {df['area'].value_counts().head()}")
        print(f"📊 Sample category values: {df['category'].value_counts().head()}")
        
        # 1. ESG Area Distribution - Use actual area data
        if 'area' in df.columns and not df['area'].isna().all():
            area_counts = df['area'].value_counts()
            print(f"📊 ESG Areas found: {len(area_counts)} - {dict(area_counts)}")
            if len(area_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                area_values = area_counts.values.tolist()
                area_names = area_counts.index.tolist()
                print(f"📊 Creating ESG Area chart with values: {area_values}")
                print(f"📊 Creating ESG Area chart with names: {area_names}")
                fig_area = px.pie(
                    values=area_values,
                    names=area_names,
                    title="ESG Area Distribution",
                    color_discrete_map={'E': '#28a745', 'S': '#ffc107', 'G': '#17a2b8'}
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_area.data:
                    if hasattr(trace, 'values') and trace.values is not None:
                        trace.values = trace.values.tolist() if hasattr(trace.values, 'tolist') else list(trace.values)
                    if hasattr(trace, 'labels') and trace.labels is not None:
                        trace.labels = trace.labels.tolist() if hasattr(trace.labels, 'tolist') else list(trace.labels)
                print(f"📊 ESG Area chart created - data type: {type(fig_area.data[0].values)}")
                print(f"📊 ESG Area chart values: {fig_area.data[0].values}")
                print(f"📊 ESG Area chart labels: {fig_area.data[0].labels}")
                viz_data['esg_area_distribution'] = fig_area.to_json()
                print(f"📊 ESG Area JSON serialized - length: {len(fig_area.to_json())}")
                print("✅ Created ESG Area Distribution with real data")
        
        # 2. Category Distribution - Use actual category data
        if 'category' in df.columns and not df['category'].isna().all():
            category_counts = df['category'].value_counts().head(15)  # Top 15 categories
            print(f"📊 Categories found: {len(category_counts)} - {dict(category_counts)}")
            if len(category_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                category_values = category_counts.values.tolist()
                category_names = category_counts.index.tolist()
                print(f"📊 Creating Category chart with values: {category_values}")
                print(f"📊 Creating Category chart with names: {category_names}")
                fig_category = px.bar(
                    x=category_values,
                    y=category_names,
                    orientation='h',
                    title="Top ESG Categories",
                    labels={'x': 'Number of Metrics', 'y': 'Category'}
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_category.data:
                    if hasattr(trace, 'x') and trace.x is not None:
                        trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                    if hasattr(trace, 'y') and trace.y is not None:
                        trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                print(f"📊 Category chart created - data type: {type(fig_category.data[0].x)}")
                print(f"📊 Category chart x values: {fig_category.data[0].x}")
                print(f"📊 Category chart y values: {fig_category.data[0].y}")
                viz_data['category_distribution'] = fig_category.to_json()
                print(f"📊 Category JSON serialized - length: {len(fig_category.to_json())}")
                print("✅ Created Category Distribution with real data")
        
        # 3. Company Distribution - Use actual company data
        if 'company' in df.columns and not df['company'].isna().all():
            company_counts = df['company'].value_counts()
            print(f"📊 Companies found: {len(company_counts)} - {dict(company_counts)}")
            if len(company_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                company_values = company_counts.values.tolist()
                company_names = company_counts.index.tolist()
                print(f"📊 Creating Company chart with values: {company_values}")
                print(f"📊 Creating Company chart with names: {company_names}")
                fig_company = px.pie(
                    values=company_values,
                    names=company_names,
                    title="Metrics by Company"
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_company.data:
                    if hasattr(trace, 'values') and trace.values is not None:
                        trace.values = trace.values.tolist() if hasattr(trace.values, 'tolist') else list(trace.values)
                    if hasattr(trace, 'labels') and trace.labels is not None:
                        trace.labels = trace.labels.tolist() if hasattr(trace.labels, 'tolist') else list(trace.labels)
                print(f"📊 Company chart created - data type: {type(fig_company.data[0].values)}")
                print(f"📊 Company chart values: {fig_company.data[0].values}")
                print(f"📊 Company chart labels: {fig_company.data[0].labels}")
                viz_data['company_distribution'] = fig_company.to_json()
                print(f"📊 Company JSON serialized - length: {len(fig_company.to_json())}")
                print("✅ Created Company Distribution with real data")
        
        # 4. Year Distribution - Use actual year data
        if 'year' in df.columns and not df['year'].isna().all():
            year_counts = df['year'].value_counts().sort_index()
            print(f"📊 Years found: {len(year_counts)} - {dict(year_counts)}")
            if len(year_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                year_x = year_counts.index.tolist()
                year_y = year_counts.values.tolist()
                print(f"📊 Creating Year chart with x: {year_x}")
                print(f"📊 Creating Year chart with y: {year_y}")
                fig_year = px.bar(
                    x=year_x,
                    y=year_y,
                    title="Metrics by Year",
                    labels={'x': 'Year', 'y': 'Number of Metrics'}
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_year.data:
                    if hasattr(trace, 'x') and trace.x is not None:
                        trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                    if hasattr(trace, 'y') and trace.y is not None:
                        trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                print(f"📊 Year chart created - data type: {type(fig_year.data[0].y)}")
                print(f"📊 Year chart x values: {fig_year.data[0].x}")
                print(f"📊 Year chart y values: {fig_year.data[0].y}")
                print(f"📊 Year chart data: x={year_x}, y={year_y}")
                viz_data['year_distribution'] = fig_year.to_json()
                print(f"📊 Year JSON serialized - length: {len(fig_year.to_json())}")
                print("✅ Created Year Distribution with real data")
        
        # 5. Importance Distribution - Use actual importance data
        if 'importance' in df.columns and not df['importance'].isna().all():
            importance_counts = df['importance'].value_counts()
            print(f"📊 Importance levels found: {len(importance_counts)} - {dict(importance_counts)}")
            if len(importance_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                importance_values = importance_counts.values.tolist()
                importance_names = importance_counts.index.tolist()
                fig_importance = px.pie(
                    values=importance_values,
                    names=importance_names,
                    title="Metrics by Importance Level",
                    color_discrete_map={'High': '#dc3545', 'Medium': '#fd7e14', 'Low': '#20c997'}
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_importance.data:
                    if hasattr(trace, 'values') and trace.values is not None:
                        trace.values = trace.values.tolist() if hasattr(trace.values, 'tolist') else list(trace.values)
                    if hasattr(trace, 'labels') and trace.labels is not None:
                        trace.labels = trace.labels.tolist() if hasattr(trace.labels, 'tolist') else list(trace.labels)
                viz_data['importance_distribution'] = fig_importance.to_json()
                print("✅ Created Importance Distribution with real data")
        
        # 6. Value Type Analysis - Use actual value data
        if 'value' in df.columns:
            value_types = df['value'].apply(lambda x: type(x).__name__).value_counts()
            print(f"📊 Value types found: {len(value_types)} - {dict(value_types)}")
            if len(value_types) > 0:
                # Convert NumPy arrays to regular Python lists
                type_values = value_types.values.tolist()
                type_names = value_types.index.tolist()
                fig_types = px.pie(
                    values=type_values,
                    names=type_names,
                    title="Value Types Distribution"
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_types.data:
                    if hasattr(trace, 'values') and trace.values is not None:
                        trace.values = trace.values.tolist() if hasattr(trace.values, 'tolist') else list(trace.values)
                    if hasattr(trace, 'labels') and trace.labels is not None:
                        trace.labels = trace.labels.tolist() if hasattr(trace.labels, 'tolist') else list(trace.labels)
                viz_data['value_types'] = fig_types.to_json()
                print("✅ Created Value Types Distribution with real data")
        
        # 7. Company-Year Heatmap - Use actual company and year data
        if 'company' in df.columns and 'year' in df.columns:
            company_year_counts = df.groupby(['company', 'year']).size().unstack(fill_value=0)
            print(f"📊 Company-Year combinations: {company_year_counts.shape}")
            if not company_year_counts.empty:
                # Convert NumPy arrays to regular Python lists
                heatmap_values = company_year_counts.values.tolist()
                heatmap_x = company_year_counts.columns.tolist()
                heatmap_y = company_year_counts.index.tolist()
                fig_heatmap = px.imshow(
                    heatmap_values,
                    x=heatmap_x,
                    y=heatmap_y,
                    title="Metrics by Company and Year",
                    labels={'x': 'Year', 'y': 'Company', 'color': 'Number of Metrics'},
                    color_continuous_scale='Blues'
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_heatmap.data:
                    if hasattr(trace, 'x') and trace.x is not None:
                        trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                    if hasattr(trace, 'y') and trace.y is not None:
                        trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                    if hasattr(trace, 'z') and trace.z is not None:
                        trace.z = trace.z.tolist() if hasattr(trace.z, 'tolist') else list(trace.z)
                viz_data['company_year_heatmap'] = fig_heatmap.to_json()
                print("✅ Created Company-Year Heatmap with real data")
        
        # 8. ESG Area by Company - Use actual area and company data
        if 'area' in df.columns and 'company' in df.columns:
            area_company_counts = df.groupby(['area', 'company']).size().unstack(fill_value=0)
            print(f"📊 Area-Company combinations: {area_company_counts.shape}")
            if not area_company_counts.empty:
                # Convert NumPy arrays to regular Python lists
                area_x = area_company_counts.index.tolist()
                area_y_lists = [area_company_counts[col].tolist() for col in area_company_counts.columns]
                fig_area_company = px.bar(
                    x=area_x,
                    y=area_y_lists,
                    title="ESG Areas by Company",
                    labels={'x': 'ESG Area', 'y': 'Number of Metrics', 'color': 'Company'},
                    barmode='group'
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_area_company.data:
                    if hasattr(trace, 'x') and trace.x is not None:
                        trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                    if hasattr(trace, 'y') and trace.y is not None:
                        trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                    if hasattr(trace, 'z') and trace.z is not None:
                        trace.z = trace.z.tolist() if hasattr(trace.z, 'tolist') else list(trace.z)
                viz_data['area_by_company'] = fig_area_company.to_json()
                print("✅ Created ESG Areas by Company with real data")
        
        # 9. Category by Company - Use actual category and company data
        if 'category' in df.columns and 'company' in df.columns:
            category_company_counts = df.groupby(['category', 'company']).size().unstack(fill_value=0)
            # Get top 10 categories
            top_categories = df['category'].value_counts().head(10).index
            print(f"📊 Top categories: {list(top_categories)}")
            if len(top_categories) > 0:
                category_company_filtered = category_company_counts.loc[top_categories]
                if not category_company_filtered.empty:
                    # Convert NumPy arrays to regular Python lists
                    category_x = category_company_filtered.index.tolist()
                    category_y_lists = [category_company_filtered[col].tolist() for col in category_company_filtered.columns]
                    fig_category_company = px.bar(
                        x=category_x,
                        y=category_y_lists,
                        title="Top Categories by Company",
                        labels={'x': 'Category', 'y': 'Number of Metrics', 'color': 'Company'},
                        barmode='group'
                    )
                    # Force conversion of any remaining NumPy arrays in the figure
                    for trace in fig_category_company.data:
                        if hasattr(trace, 'x') and trace.x is not None:
                            trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                        if hasattr(trace, 'y') and trace.y is not None:
                            trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                    viz_data['category_by_company'] = fig_category_company.to_json()
                    print("✅ Created Categories by Company with real data")
        
        # 10. Value Distribution - Use actual numeric values
        if 'value' in df.columns:
            numeric_values = pd.to_numeric(df['value'], errors='coerce')
            if not numeric_values.isna().all():
                valid_values = numeric_values.dropna()
                print(f"📊 Numeric values found: {len(valid_values)}")
                if len(valid_values) > 0:
                    # Convert NumPy arrays to regular Python lists
                    value_dist_values = valid_values.tolist()
                    fig_value_dist = px.histogram(
                        x=value_dist_values,
                        title="Distribution of Numeric Values",
                        labels={'x': 'Value', 'y': 'Count'},
                        nbins=20
                    )
                    # Force conversion of any remaining NumPy arrays in the figure
                    for trace in fig_value_dist.data:
                        if hasattr(trace, 'x') and trace.x is not None:
                            trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                        if hasattr(trace, 'y') and trace.y is not None:
                            trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                    viz_data['value_distribution'] = fig_value_dist.to_json()
                    print("✅ Created Value Distribution with real data")
        
        # 11. Unit Distribution - Use actual unit data
        if 'unit' in df.columns and not df['unit'].isna().all():
            unit_counts = df['unit'].value_counts().head(10)
            print(f"📊 Units found: {len(unit_counts)} - {dict(unit_counts)}")
            if len(unit_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                unit_values = unit_counts.values.tolist()
                unit_names = unit_counts.index.tolist()
                fig_unit = px.bar(
                    x=unit_values,
                    y=unit_names,
                    orientation='h',
                    title="Top Units Used",
                    labels={'x': 'Number of Metrics', 'y': 'Unit'}
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_unit.data:
                    if hasattr(trace, 'x') and trace.x is not None:
                        trace.x = trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x)
                    if hasattr(trace, 'y') and trace.y is not None:
                        trace.y = trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y)
                viz_data['unit_distribution'] = fig_unit.to_json()
                print("✅ Created Unit Distribution with real data")
        
        # 12. Metric Type Analysis - Use actual type data
        if 'type' in df.columns and not df['type'].isna().all():
            type_counts = df['type'].value_counts()
            print(f"📊 Types found: {len(type_counts)} - {dict(type_counts)}")
            if len(type_counts) > 0:
                # Convert NumPy arrays to regular Python lists
                type_values = type_counts.values.tolist()
                type_names = type_counts.index.tolist()
                fig_type = px.pie(
                    values=type_values,
                    names=type_names,
                    title="Metrics by Type"
                )
                # Force conversion of any remaining NumPy arrays in the figure
                for trace in fig_type.data:
                    if hasattr(trace, 'values') and trace.values is not None:
                        trace.values = trace.values.tolist() if hasattr(trace.values, 'tolist') else list(trace.values)
                    if hasattr(trace, 'labels') and trace.labels is not None:
                        trace.labels = trace.labels.tolist() if hasattr(trace.labels, 'tolist') else list(trace.labels)
                viz_data['type_distribution'] = fig_type.to_json()
                print("✅ Created Type Distribution with real data")
        
        print(f"🎉 Created {len(viz_data)} visualizations with real data")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()
    
    return viz_data

def create_benchmarking_data():
    """Create direct comparison benchmarking between companies (Excel format)"""
    benchmark_data = {}
    
    # Get all metrics for comparison
    all_metrics = []
    for key, data in esg_data.items():
        metrics = extract_metrics_from_json(data['data'])
        for metric in metrics:
            metric['company'] = data['company']
            metric['year'] = data['year']
            all_metrics.append(metric)
    
    if all_metrics:
        # Create comparison table data (like Excel format)
        comparison_data = []
        
        # Group metrics by name for comparison
        metric_groups = {}
        for metric in all_metrics:
            metric_name = metric.get('metric_name', metric.get('metric', ''))
            if metric_name not in metric_groups:
                metric_groups[metric_name] = {}
            metric_groups[metric_name][metric['company']] = metric
        
        # Create comparison entries
        for metric_name, company_data in metric_groups.items():
            amazon_data = company_data.get('Amazon', {})
            alibaba_data = company_data.get('Alibaba', {})
            
            comparison_entry = {
                'metric_name': metric_name,
                'amazon_value': amazon_data.get('value', 'N/A'),
                'alibaba_value': alibaba_data.get('value', 'N/A'),
                'amazon_unit': amazon_data.get('unit', ''),
                'alibaba_unit': alibaba_data.get('unit', ''),
                'category': amazon_data.get('category', alibaba_data.get('category', '')),
                'area': amazon_data.get('area', alibaba_data.get('area', '')),
                'subcategory': amazon_data.get('subcategory', alibaba_data.get('subcategory', '')),
                'notes': amazon_data.get('description', alibaba_data.get('description', ''))
            }
            comparison_data.append(comparison_entry)
        
        # Create comparison chart
        if comparison_data:
            # Prepare data for chart
            chart_data = []
            for entry in comparison_data:
                if entry['amazon_value'] != 'N/A' or entry['alibaba_value'] != 'N/A':
                    chart_data.append({
                        'metric': entry['metric_name'],
                        'amazon': entry['amazon_value'],
                        'alibaba': entry['alibaba_value'],
                        'category': entry['category']
                    })
            
            if chart_data:
                # Create comparison chart
                df = pd.DataFrame(chart_data)
                
                # Create bar chart for comparison
                fig_comparison = px.bar(
                    df,
                    x='metric',
                    y=['amazon', 'alibaba'],
                    title="ESG Metrics Comparison - Amazon vs Alibaba",
                    barmode='group',
                    labels={'value': 'Metric Value', 'variable': 'Company'}
                )
                benchmark_data["direct_comparison"] = fig_comparison.to_json()
        
        # Store comparison data for table display
        benchmark_data["comparison_table"] = comparison_data
    
    return benchmark_data

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', companies=companies, esg_data=esg_data)

@app.route('/api/data')
def get_data():
    """API endpoint to get ESG data"""
    print(f"📊 API /api/data called")
    print(f"📊 Global esg_data keys: {list(esg_data.keys())}")
    print(f"📊 Global esg_data length: {len(esg_data)}")
    if esg_data:
        sample_key = list(esg_data.keys())[0]
        print(f"📊 Sample entry structure: {list(esg_data[sample_key].keys())}")
        if 'data' in esg_data[sample_key]:
            print(f"📊 Sample data.metrics length: {len(esg_data[sample_key]['data'].get('metrics', []))}")
    
    # Return Excel data if available, otherwise fall back to JSON data
    return jsonify(esg_data)

@app.route('/api/visualizations')
def get_visualizations():
    """API endpoint to get visualizations"""
    print("🔄 Creating visualizations...")
    try:
        print(f"📊 Input data keys: {list(esg_data.keys())}")
        print(f"📊 Sample data structure: {list(esg_data.keys())[0] if esg_data else 'No data'}")
        if esg_data:
            sample_key = list(esg_data.keys())[0]
            print(f"📊 Sample entry structure: {list(esg_data[sample_key].keys())}")
            if 'data' in esg_data[sample_key]:
                print(f"📊 Sample data.metrics length: {len(esg_data[sample_key]['data'].get('metrics', []))}")
        
        viz_data = create_visualizations(esg_data)
        print(f"✅ Created {len(viz_data)} visualizations")
        
        # Debug: Show what's being sent
        print(f"📊 Visualization keys being sent: {list(viz_data.keys())}")
        for key, value in viz_data.items():
            print(f"📊 {key}: {type(value)} - {len(str(value))} characters")
            if key == 'esg_area_distribution':
                # Parse and show the actual data being sent
                import json
                try:
                    parsed = json.loads(value)
                    if 'data' in parsed and len(parsed['data']) > 0:
                        first_trace = parsed['data'][0]
                        print(f"📊 ESG Area data structure: {list(first_trace.keys())}")
                        if 'values' in first_trace:
                            print(f"📊 ESG Area values type: {type(first_trace['values'])}")
                            print(f"📊 ESG Area values: {first_trace['values']}")
                        if 'labels' in first_trace:
                            print(f"📊 ESG Area labels: {first_trace['labels']}")
                except Exception as e:
                    print(f"❌ Error parsing ESG Area data: {e}")
        
        return jsonify(viz_data)
    except Exception as e:
        print(f"❌ Error in visualization API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/benchmarking')
def get_benchmarking():
    """API endpoint to get benchmarking data"""
    print("🔄 Creating benchmarking data...")
    try:
        # Return available reports for comparison
        available_reports = []
        for key, data in esg_data.items():
            available_reports.append({
                'key': key,
                'company': data.get('company', ''),
                'year': data.get('year', ''),
                'metrics_count': len(data.get('data', {}).get('metrics', []))
            })
        
        print(f"✅ Created benchmarking data for {len(available_reports)} reports")
        return jsonify({
            'available_reports': available_reports,
            'total_reports': len(available_reports)
        })
    except Exception as e:
        print(f"❌ Error in benchmarking API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/exploration')
def exploration():
    """Data exploration page"""
    return render_template('exploration.html', companies=companies, esg_data=esg_data)

@app.route('/visualization')
def visualization():
    """Data visualization page"""
    return render_template('visualization.html', companies=companies, esg_data=esg_data)

@app.route('/benchmarking')
def benchmarking():
    """Benchmarking page"""
    return render_template('benchmarking.html', companies=companies, esg_data=esg_data)

@app.route('/api/metrics/<company>/<year>')
def get_company_metrics(company, year):
    """Get metrics for a specific company and year"""
    # If using Excel data, return all metrics (since they're comparison data)
    key = f"{company}_{year}"
    if key in esg_data:
        metrics = extract_metrics_from_json(esg_data[key]['data'])
        return jsonify(metrics)
    return jsonify([])

@app.route('/api/search')
def search_metrics():
    """Search metrics across all companies - Only search Excel metrics"""
    query = request.args.get('q', '').lower()
    results = []
    
    # Only search in Excel-converted data
    for key, data in esg_data.items():
        metrics = extract_metrics_from_json(data['data'])
        for metric in metrics:
            if (query in metric['metric_name'].lower() or 
                query in metric['category'].lower() or
                query in str(metric['value']).lower() or
                query in metric['description'].lower()):
                results.append(metric)
    
    return jsonify(results)

@app.route('/api/comparison/<company1>/<year1>/<company2>/<year2>')
def get_comparison_visualizations(company1, year1, company2, year2):
    """API endpoint to get dual-axis comparison visualizations"""
    print(f"🔄 Creating comparison visualizations for {company1} {year1} vs {company2} {year2}")
    try:
        # Find the two reports
        report1 = None
        report2 = None
        
        for key, data in esg_data.items():
            if data.get('company') == company1 and data.get('year') == year1:
                report1 = data
            elif data.get('company') == company2 and data.get('year') == year2:
                report2 = data
        
        if not report1 or not report2:
            return jsonify({"error": "One or both reports not found"}), 404
        
        # Create dual-axis visualizations
        viz_data = create_dual_axis_visualizations(report1, report2)
        
        print(f"✅ Created {len(viz_data)} comparison visualizations")
        return jsonify(viz_data)
    except Exception as e:
        print(f"❌ Error in comparison API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/dynamic-comparison/<company1>/<year1>/<company2>/<year2>')
def get_dynamic_comparison_analysis(company1, year1, company2, year2):
    """API endpoint to get dynamic LLM-based comparison analysis"""
    print(f"🔄 Creating dynamic comparison analysis for {company1} {year1} vs {company2} {year2}")
    try:
        # Find the two reports
        report1 = None
        report2 = None
        
        for key, data in esg_data.items():
            if data.get('company') == company1 and data.get('year') == year1:
                report1 = data
            elif data.get('company') == company2 and data.get('year') == year2:
                report2 = data
        
        if not report1 or not report2:
            return jsonify({"error": "One or both reports not found"}), 404
        
        # Extract metrics from both reports
        metrics1 = extract_metrics_from_json(report1['data'])
        metrics2 = extract_metrics_from_json(report2['data'])
        
        print(f"📊 Found {len(metrics1)} metrics for {company1} {year1}")
        print(f"📊 Found {len(metrics2)} metrics for {company2} {year2}")
        
        # Use the dynamic comparison analyzer
        analysis = comparison_analyzer.analyze_pair(
            metrics1, metrics2, 
            company1, year1, 
            company2, year2
        )
        
        print(f"✅ Created dynamic comparison analysis")
        return jsonify(analysis)
    except Exception as e:
        print(f"❌ Error in dynamic comparison API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/unit_conversion_results')
def get_unit_conversion_results():
    """API endpoint to serve comprehensive unit conversion results"""
    try:
        # Load the comprehensive unit conversion results
        current_dir = os.path.dirname(os.path.abspath(__file__))
        conversion_file = os.path.join(current_dir, "comprehensive_conversion_results.json")
        
        if os.path.exists(conversion_file):
            with open(conversion_file, 'r', encoding='utf-8') as f:
                conversion_results = json.load(f)
            
            print(f"✅ Served unit conversion results for {len(conversion_results)} patterns")
            return jsonify(conversion_results)
        else:
            print("⚠️ Unit conversion results file not found")
            return jsonify({}), 404
            
    except Exception as e:
        print(f"❌ Error serving unit conversion results: {e}")
        return jsonify({'error': str(e)}), 500

def create_dual_axis_visualizations(report1, report2):
    """Create dual-axis visualizations for comparing two reports"""
    viz_data = {}
    
    try:
        # Extract metrics from both reports
        metrics1 = extract_metrics_from_json(report1['data'])
        metrics2 = extract_metrics_from_json(report2['data'])
        
        # 1. ESG Area Comparison with dual y-axis
        area_counts1 = {}
        area_counts2 = {}
        
        for metric in metrics1:
            area = metric.get('area', 'Unknown')
            area_counts1[area] = area_counts1.get(area, 0) + 1
        
        for metric in metrics2:
            area = metric.get('area', 'Unknown')
            area_counts2[area] = area_counts2.get(area, 0) + 1
        
        all_areas = list(set(list(area_counts1.keys()) + list(area_counts2.keys())))
        
        fig_area = {
            'data': [
                {
                    'x': all_areas,
                    'y': [area_counts1.get(area, 0) for area in all_areas],
                    'name': f"{report1['company']} ({report1['year']})",
                    'type': 'bar',
                    'yaxis': 'y',
                    'marker': {'color': '#667eea'}
                },
                {
                    'x': all_areas,
                    'y': [area_counts2.get(area, 0) for area in all_areas],
                    'name': f"{report2['company']} ({report2['year']})",
                    'type': 'bar',
                    'yaxis': 'y2',
                    'marker': {'color': '#11998e'}
                }
            ],
            'layout': {
                'title': 'ESG Area Distribution Comparison',
                'xaxis': {'title': 'ESG Area'},
                'yaxis': {
                    'title': f"{report1['company']} ({report1['year']})",
                    'side': 'left',
                    'showgrid': False
                },
                'yaxis2': {
                    'title': f"{report2['company']} ({report2['year']})",
                    'side': 'right',
                    'overlaying': 'y',
                    'showgrid': False
                },
                'legend': {'x': 0, 'y': 1}
            }
        }
        viz_data['dual_esg_area'] = fig_area
        
        # 2. Category Comparison with dual y-axis
        category_counts1 = {}
        category_counts2 = {}
        
        for metric in metrics1:
            category = metric.get('category', 'Unknown')
            category_counts1[category] = category_counts1.get(category, 0) + 1
        
        for metric in metrics2:
            category = metric.get('category', 'Unknown')
            category_counts2[category] = category_counts2.get(category, 0) + 1
        
        # Get top 10 categories
        all_categories = list(set(list(category_counts1.keys()) + list(category_counts2.keys())))
        top_categories = sorted(all_categories, key=lambda x: max(category_counts1.get(x, 0), category_counts2.get(x, 0)), reverse=True)[:10]
        
        fig_category = {
            'data': [
                {
                    'x': [category_counts1.get(cat, 0) for cat in top_categories],
                    'y': top_categories,
                    'name': f"{report1['company']} ({report1['year']})",
                    'type': 'bar',
                    'orientation': 'h',
                    'yaxis': 'y',
                    'marker': {'color': '#667eea'}
                },
                {
                    'x': [category_counts2.get(cat, 0) for cat in top_categories],
                    'y': top_categories,
                    'name': f"{report2['company']} ({report2['year']})",
                    'type': 'bar',
                    'orientation': 'h',
                    'yaxis': 'y2',
                    'marker': {'color': '#11998e'}
                }
            ],
            'layout': {
                'title': 'Top Categories Comparison',
                'xaxis': {'title': 'Number of Metrics'},
                'yaxis': {
                    'title': f"{report1['company']} ({report1['year']})",
                    'side': 'left',
                    'showgrid': False
                },
                'yaxis2': {
                    'title': f"{report2['company']} ({report2['year']})",
                    'side': 'right',
                    'overlaying': 'y',
                    'showgrid': False
                },
                'legend': {'x': 0, 'y': 1}
            }
        }
        viz_data['dual_category'] = fig_category
        
        # 3. Value Comparison (for numeric metrics)
        numeric_values1 = []
        numeric_values2 = []
        
        for metric in metrics1:
            try:
                value = float(metric.get('value', 0))
                if value > 0:
                    numeric_values1.append(value)
            except:
                pass
        
        for metric in metrics2:
            try:
                value = float(metric.get('value', 0))
                if value > 0:
                    numeric_values2.append(value)
            except:
                pass
        
        if numeric_values1 and numeric_values2:
            fig_value = {
                'data': [
                    {
                        'x': numeric_values1,
                        'name': f"{report1['company']} ({report1['year']})",
                        'type': 'histogram',
                        'opacity': 0.7,
                        'yaxis': 'y',
                        'marker': {'color': '#667eea'}
                    },
                    {
                        'x': numeric_values2,
                        'name': f"{report2['company']} ({report2['year']})",
                        'type': 'histogram',
                        'opacity': 0.7,
                        'yaxis': 'y2',
                        'marker': {'color': '#11998e'}
                    }
                ],
                'layout': {
                    'title': 'Numeric Values Distribution Comparison',
                    'xaxis': {'title': 'Value'},
                    'yaxis': {
                        'title': f"{report1['company']} ({report1['year']})",
                        'side': 'left',
                        'showgrid': False
                    },
                    'yaxis2': {
                        'title': f"{report2['company']} ({report2['year']})",
                        'side': 'right',
                        'overlaying': 'y',
                        'showgrid': False
                    },
                    'barmode': 'overlay',
                    'legend': {'x': 0, 'y': 1}
                }
            }
            viz_data['dual_value'] = fig_value
        
        print(f"✅ Created {len(viz_data)} dual-axis visualizations")
        
    except Exception as e:
        print(f"❌ Error creating dual-axis visualizations: {e}")
        import traceback
        traceback.print_exc()
    
    return viz_data

if __name__ == '__main__':
    # Load data on startup
    load_esg_data()
    
    # Count total metrics from Excel data
    total_metrics = 0
    for key, data in esg_data.items():
        metrics = extract_metrics_from_json(data['data'])
        total_metrics += len(metrics)
    
    print(f"✅ Loaded Excel-converted data: {len(esg_data)} datasets")
    print(f"📊 Total metrics: {total_metrics}")
    print(f"📊 Companies: {companies}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 