# NASS Corn Yield Explorer
# Uses USDA NASS data to explore corn yield trends across U.S. states

import gradio as gr
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

# ── CONFIGURE GEMINI ───────────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-2.5-pro")

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
df = pd.read_csv("nass_corn_clean.csv")
df = df[df["state"] != "Other States"]
df = df.groupby(["state", "year"])["yield_bu_acre"].max().reset_index()
ALL_STATES = sorted(df["state"].unique().tolist())

# ── CHART FUNCTIONS ────────────────────────────────────────────────────────────

def make_trend_chart(state):
    """
    Generate a scatter plot with OLS trend line for a given state.
     - X-axis: Year
     - Y-axis: Corn yield (bushels per acre)"""
    filtered = df[df["state"] == state].sort_values("year")
    fig = px.scatter(
        filtered, x="year", y="yield_bu_acre",
        trendline="ols",
        title=f"Corn Yield — {state} (2000–2025)",
        labels={"year": "Year", "yield_bu_acre": "Yield (bu/acre)"},
        color_discrete_sequence=["#2E7D32"]
    )
    fig.update_traces(marker=dict(size=7))
    fig.update_layout(
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="white",
        hovermode="x unified"
    )
    return fig

def make_choropleth(year):
    """Generate a national choropleth map for a given year."""
    latest = df[df["year"] == int(year)].copy()
    # dictionary mapping full state names to two-letter abbreviations
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
        'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    latest["abbrev"] = latest["state"].map(state_abbrev)
    latest = latest.dropna(subset=["abbrev"])
    fig = px.choropleth(
        latest, locations="abbrev", locationmode="USA-states",
        color="yield_bu_acre", scope="usa",
        color_continuous_scale="Greens",
        title=f"Corn Yield by State — {year}",
        labels={"yield_bu_acre": "Yield (bu/acre)"}
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def make_summary(state):
    """Return markdown summary stats for a given state."""
    s = df[df["state"] == state]
    avg = s["yield_bu_acre"].mean()
    best_row = s.loc[s["yield_bu_acre"].idxmax()]
    worst_row = s.loc[s["yield_bu_acre"].idxmin()]
    recent = s[s["year"] >= 2020]["yield_bu_acre"].mean()
    trend = "↑ improving" if recent > avg else "↓ below long-term average"
    return (
        f"### {state} Summary\n"
        f"- **Average yield (2000–2025):** {avg:.1f} bu/acre\n"
        f"- **Peak:** {best_row['yield_bu_acre']:.0f} bu/acre ({int(best_row['year'])})\n"
        f"- **Lowest:** {worst_row['yield_bu_acre']:.0f} bu/acre ({int(worst_row['year'])})\n"
        f"- **Recent trend (2020–2025):** {trend}"
    )

# ── AI INSIGHT ─────────────────────────────────────────────────────────────────

def generate_insight(state):
    """Use Gemini 2.5 Pro to generate a plain-English insight for a given state."""
    s = df[df["state"] == state]
    avg = s["yield_bu_acre"].mean()
    best_row = s.loc[s["yield_bu_acre"].idxmax()]
    recent = s[s["year"] >= 2020]["yield_bu_acre"].mean()
    trend = "improving" if recent > avg else "declining"

    response = gemini.generate_content(
        f"You are an agricultural data analyst. Write 2-3 sentences of plain-English "
        f"insight for a farmer or policymaker about this USDA corn yield data.\n\n"
        f"State: {state}\n"
        f"Average yield (2000–2025): {avg:.1f} bu/acre\n"
        f"Peak yield: {best_row['yield_bu_acre']:.0f} bu/acre in {int(best_row['year'])}\n"
        f"Recent trend: {trend}\n\n"
        f"Be specific and practical, not generic."
    )
    return response.text

# ── REVENUE ESTIMATOR ──────────────────────────────────────────────────────────

def estimate_revenue(state, acreage, price_per_bushel):
    """Estimate gross farm revenue based on latest yield, acreage, and price."""
    latest_year = df["year"].max()
    latest_yield = df[
        (df["state"] == state) & (df["year"] == latest_year)
    ]["yield_bu_acre"]

    if latest_yield.empty:
        return "No data available for this state."

    yield_val = latest_yield.values[0]
    total_bushels = yield_val * acreage
    gross_revenue = total_bushels * price_per_bushel
    
    state_avg = df[df["state"] == state]["yield_bu_acre"].mean()

    if yield_val >= state_avg * 1.1:
        risk = "🟢 Low Risk — Above average yield year"
    elif yield_val >= state_avg * 0.9:
        risk = "🟡 Medium Risk — Near average yield year"
    else:
        risk = "🔴 High Risk — Below average yield year"
    return (
    f"### Revenue Estimate (based on {int(latest_year)} yield)\n"
    f"- **Yield used:** {yield_val:.0f} bu/acre *(most recent year)*\n"
    f"- **Total bushels:** {total_bushels:,.0f}\n"
    f"- **Estimated gross revenue:** ${gross_revenue:,.0f}\n"
    f"- **Risk:** {risk}"
)

# ── GRADIO UI ──────────────────────────────────────────────────────────────────

CSS = """
#header { background: #1B5E20; padding: 16px 24px; border-radius: 8px; margin-bottom: 12px; }
#header h1 { color: white; margin: 0; font-size: 1.5rem; }
#header p  { color: #C8E6C9; margin: 4px 0 0; font-size: 0.9rem; }
"""

with gr.Blocks(css=CSS, theme=gr.themes.Soft()) as demo:

    gr.HTML("""
    <div id="header">
      <h1>🌾 NASS Corn Yield Explorer</h1>
      <p>U.S. corn yield trends from USDA National Agricultural Statistics Service (2000–2025)</p>
    </div>
    """)

    # ── CONTROLS ───────────────────────────────────────────────────────────────
    with gr.Row():
        state_dd = gr.Dropdown(
            choices=ALL_STATES, value="Iowa", label="State"
        )
        year_slider = gr.Slider(
            minimum=2000, maximum=2025, value=2025,
            step=1, label="Map Year"
        )

    run_btn = gr.Button("🔍 Update Charts", variant="primary")

    # ── CHARTS ─────────────────────────────────────────────────────────────────
    with gr.Row():
        trend_plot = gr.Plot(label="Yield Over Time")
        choro_plot = gr.Plot(label="National Map")

    summary_box = gr.Markdown()

    # ── AI INSIGHT ─────────────────────────────────────────────────────────────
    gr.Markdown("---")
    gr.Markdown("### 🤖 AI Insight (Gemini 2.5 Pro)")
    insight_btn = gr.Button("Generate AI Insight", variant="secondary")
    insight_box = gr.Textbox(label="AI Analysis", lines=4)

    # ── REVENUE ESTIMATOR ──────────────────────────────────────────────────────
    gr.Markdown("---")
    gr.Markdown("### 💰 Farm Revenue Estimator")
    with gr.Row():
        acreage_input = gr.Number(value=500, label="Acreage (acres)")
        price_input = gr.Number(value=4.50, label="Price per Bushel ($)")
    revenue_btn = gr.Button("Calculate Revenue", variant="secondary")
    revenue_box = gr.Markdown()

    # ── EVENT HANDLERS ─────────────────────────────────────────────────────────
    def update_charts(state, year):
        return make_trend_chart(state), make_choropleth(year), make_summary(state)

    run_btn.click(
        fn=update_charts,
        inputs=[state_dd, year_slider],
        outputs=[trend_plot, choro_plot, summary_box]
    )
    insight_btn.click(
        fn=generate_insight,
        inputs=[state_dd],
        outputs=[insight_box]
    )
    revenue_btn.click(
        fn=estimate_revenue,
        inputs=[state_dd, acreage_input, price_input],
        outputs=[revenue_box]
    )

    # Auto-load on startup
    demo.load(
        fn=update_charts,
        inputs=[state_dd, year_slider],
        outputs=[trend_plot, choro_plot, summary_box]
    )

    gr.Markdown("---")
    gr.Markdown("*Data source: USDA National Agricultural Statistics Service (NASS) | Built with Gradio + Gemini 2.5 Pro*")

demo.launch()