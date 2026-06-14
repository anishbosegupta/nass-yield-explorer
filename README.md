# NASS Yield Explorer

A USDA Hackathon project for exploring U.S. corn yield trends using interactive visualizations and AI-enhanced explanations.

## Overview

`nass-yield-explorer` is a Gradio web application that helps users explore USDA NASS corn yield data from 2000 to 2025 by state. It includes:

- interactive trend visualizations
- a national choropleth map
- state-level summary statistics
- AI-generated insights via Gemini 2.5 Pro
- a simple farm revenue estimator based on yield, acreage, and price

## Features

- **State trend chart** with scatter plot and OLS regression line
- **Choropleth map** of U.S. corn yield by state and year
- **State summary panel** showing average, peak, and lowest yields
- **AI insight generator** to summarize yield performance for a selected state
- **Revenue estimator** for gross revenue based on latest yield, acreage, and price

## Technology Stack

- **Python**
- **pandas** for dataset loading and filtering
- **Plotly Express** for interactive charts and maps
- **Gradio** for the web UI
- **Google Gemini 2.5 Pro** for AI insight generation
- **USDA NASS Quick Stats** served in `nass_corn_clean.csv`

## Data

The app uses `nass_corn_clean.csv` as its primary dataset. The dataset is filtered to remove non-state rows and is expected to include at least these columns:

- `state`
- `year`
- `yield_bu_acre`

## Installation

1. Create or activate a Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install required packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

> Note: The current app uses the `google.generativeai` package for Gemini integration. If you choose to update the app later, consider migrating to the newer `google.genai` package.

## Configuration

The AI insight feature requires a Gemini API key. Set the environment variable before launching:

### PowerShell

```powershell
$env:GEMINI_API_KEY = "your_api_key_here"
python app.py
```

### CMD

```cmd
set GEMINI_API_KEY=your_api_key_here
python app.py
```

## Running the App

From the project root:

```powershell
python app.py
```

Then open the local Gradio URL shown in the terminal.

## Usage

1. Select a state from the dropdown.
2. Adjust the map year slider to view the national choropleth.
3. Click **Update Charts** to refresh the trend plot, map, and summary.
4. Click **Generate AI Insight** to receive a text summary of the selected state's corn yield.
5. Enter acreage and price per bushel, then click **Calculate Revenue** to estimate gross farm revenue.

## Notes

- The app calculates revenue using the latest available yield in the dataset.
- If the selected state has no data for the latest year, revenue estimation may return an error or no result.
- The AI insight feature depends on Gemini credentials and may not work without a valid API key.

## Improvements

Potential future upgrades:

- add year fallback for states missing the latest year
- add input validation for acreage and price
- migrate Gemini calls to the newer `google.genai` SDK
- add a `requirements.txt` or `pyproject.toml` for dependency management
- add a unit test suite for chart and calculation functions
