# nass-yield-explorer
Corn yeild explorer for USDA Hackathon
# NASS Corn Yield Explorer

An interactive Gradio web app for exploring USDA corn yield trends across U.S. states (2000–2025), with AI-powered insights using Gemini 2.5 Pro.

## Stack
- **Python + pandas** — data cleaning and transformation
- **Databricks** — exploratory data analysis and visualizations
- **Gradio** — interactive web app
- **Plotly** — trend charts and choropleth map
- **Google Gemini 2.5 Pro** — AI-generated crop insights
- **Data source** — USDA NASS Quick Stats (Survey, State-level, Corn Grain Yield)

## Features
- State-by-state corn yield trend chart with OLS regression line
- National choropleth map by year
- Summary stats (average, peak, lowest yield)
- AI insight generator powered by Gemini 2.5 Pro
- Farm revenue estimator (yield × acreage × price per bushel)

## Setup

### 1. Install dependencies
