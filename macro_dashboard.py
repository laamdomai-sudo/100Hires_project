from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Macro Dashboard: Offline CSV Mode", layout="wide")
st.title("Macro Dashboard: CPI, Fed Rate, Real Rate, DXY, Gold")
st.caption("Offline mode: read local CSV files only (no network calls)")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "local_macro"
REQUIRED_FILES = {
    "cpi": DATA_DIR / "cpi.csv",
    "fed_funds": DATA_DIR / "fed_funds.csv",
    "dxy": DATA_DIR / "dxy.csv",
    "gold_usd_oz": DATA_DIR / "gold.csv",
}


@st.cache_data(ttl=0)
def read_local_series(path: Path, value_col_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=[value_col_name])

    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=[value_col_name])

    columns_lower = {c.lower(): c for c in df.columns}
    if "date" in columns_lower:
        date_col = columns_lower["date"]
    else:
        date_col = df.columns[0]

    if "value" in columns_lower:
        value_col = columns_lower["value"]
    else:
        value_col = df.columns[-1]

    # Support year-only inputs like 2000, 2001 by casting to string first.
    df[date_col] = pd.to_datetime(df[date_col].astype(str), errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[date_col, value_col]).rename(columns={date_col: "date", value_col: value_col_name})
    return df.set_index("date").sort_index()[[value_col_name]]


def read_uploaded_series(uploaded_file, value_col_name: str) -> pd.DataFrame:
    if uploaded_file is None:
        return pd.DataFrame(columns=[value_col_name])
    df = pd.read_csv(uploaded_file)
    if df.empty:
        return pd.DataFrame(columns=[value_col_name])

    columns_lower = {c.lower(): c for c in df.columns}
    date_col = columns_lower["date"] if "date" in columns_lower else df.columns[0]
    value_col = columns_lower["value"] if "value" in columns_lower else df.columns[-1]
    # Support year-only inputs like 2000, 2001 by casting to string first.
    df[date_col] = pd.to_datetime(df[date_col].astype(str), errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[date_col, value_col]).rename(columns={date_col: "date", value_col: value_col_name})
    return df.set_index("date").sort_index()[[value_col_name]]


def build_dataset_local(cpi_src=None, fed_src=None, dxy_src=None, gold_src=None) -> pd.DataFrame:
    cpi = read_uploaded_series(cpi_src, "cpi") if cpi_src is not None else read_local_series(REQUIRED_FILES["cpi"], "cpi")
    fed = read_uploaded_series(fed_src, "fed_funds") if fed_src is not None else read_local_series(REQUIRED_FILES["fed_funds"], "fed_funds")
    dxy = read_uploaded_series(dxy_src, "dxy") if dxy_src is not None else read_local_series(REQUIRED_FILES["dxy"], "dxy")
    gold = read_uploaded_series(gold_src, "gold_usd_oz") if gold_src is not None else read_local_series(REQUIRED_FILES["gold_usd_oz"], "gold_usd_oz")

    df = pd.concat([cpi, fed, dxy, gold], axis=1).infer_objects(copy=False).ffill()
    if df.empty or "cpi" not in df.columns or "fed_funds" not in df.columns:
        return pd.DataFrame()
    df["inflation_yoy"] = df["cpi"].pct_change(12) * 100
    df["real_rate"] = df["fed_funds"] - df["inflation_yoy"]
    return df.dropna(subset=["inflation_yoy", "fed_funds", "real_rate", "dxy", "gold_usd_oz"])


st.sidebar.header("Data source")
use_upload = st.sidebar.toggle("Upload CSV files", value=False)

uploaded_cpi = uploaded_fed = uploaded_dxy = uploaded_gold = None
if use_upload:
    st.sidebar.caption("Upload CSV with columns: `date,value`")
    uploaded_cpi = st.sidebar.file_uploader("CPI CSV", type=["csv"], key="cpi_csv")
    uploaded_fed = st.sidebar.file_uploader("Fed Funds CSV", type=["csv"], key="fed_csv")
    uploaded_dxy = st.sidebar.file_uploader("DXY CSV", type=["csv"], key="dxy_csv")
    uploaded_gold = st.sidebar.file_uploader("Gold CSV", type=["csv"], key="gold_csv")

df = build_dataset_local(uploaded_cpi, uploaded_fed, uploaded_dxy, uploaded_gold)

if df.empty:
    missing = [str(path) for path in REQUIRED_FILES.values() if not path.exists()]
    st.error("Local CSV data not available or invalid.")
    if use_upload:
        st.write("Please upload all 4 CSV files in the sidebar (CPI, Fed Funds, DXY, Gold).")
    else:
        st.write("Expected files:")
        st.code("\n".join(str(path) for path in REQUIRED_FILES.values()))
    st.write("Required CSV format (at least these columns):")
    st.code("date,value")
    if missing and not use_upload:
        st.write("Missing files:")
        st.code("\n".join(missing))
    st.stop()

timeline_start = pd.Timestamp("2000-01-01")
timeline_end = pd.Timestamp("2026-12-31")
df = df.loc[(df.index >= timeline_start) & (df.index <= timeline_end)]

if df.empty:
    st.error("No data available in the selected timeline (2000-2026).")
    st.stop()

st.sidebar.header("Configuration")
view_mode = st.sidebar.selectbox(
    "Timeline view",
    options=["Full timeline (2000-2026)", "2000-2008", "2009-2019", "2020-2026", "Custom range"],
    index=0,
)

if view_mode == "2000-2008":
    default_start, default_end = pd.Timestamp("2000-01-01"), pd.Timestamp("2008-12-31")
elif view_mode == "2009-2019":
    default_start, default_end = pd.Timestamp("2009-01-01"), pd.Timestamp("2019-12-31")
elif view_mode == "2020-2026":
    default_start, default_end = pd.Timestamp("2020-01-01"), pd.Timestamp("2026-12-31")
else:
    default_start, default_end = df.index.min(), df.index.max()

start_date = st.sidebar.date_input(
    "Start date",
    value=default_start.date(),
    min_value=df.index.min().date(),
    max_value=df.index.max().date(),
)
end_date = st.sidebar.date_input(
    "End date",
    value=default_end.date(),
    min_value=df.index.min().date(),
    max_value=df.index.max().date(),
)

if start_date > end_date:
    st.error("Start date must be earlier than or equal to end date.")
    st.stop()

filtered = df.loc[(df.index.date >= start_date) & (df.index.date <= end_date)].copy()

st.subheader("1) CPI YoY Inflation, Fed Funds Rate, and Real Rate")
fig_rates = go.Figure()
fig_rates.add_trace(go.Scatter(x=filtered.index, y=filtered["inflation_yoy"], mode="lines", name="Inflation YoY (%)", line=dict(width=2)))
fig_rates.add_trace(go.Scatter(x=filtered.index, y=filtered["fed_funds"], mode="lines", name="Fed Funds Rate (%)", line=dict(width=2)))
fig_rates.add_trace(go.Scatter(x=filtered.index, y=filtered["real_rate"], mode="lines", name="Real Rate (%)", line=dict(width=3)))
fig_rates.add_hline(y=0, line_dash="dot", line_width=1, line_color="gray")
fig_rates.update_layout(
    template="plotly_dark",
    height=520,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Percent (%)",
    xaxis=dict(rangeslider=dict(visible=True)),
)
st.plotly_chart(fig_rates, use_container_width=True)

st.subheader("2) DXY Index and Gold Price")
fig_assets = go.Figure()
fig_assets.add_trace(go.Scatter(x=filtered.index, y=filtered["dxy"], mode="lines", name="DXY (DTWEXBGS)", line=dict(width=2)))
fig_assets.add_trace(
    go.Scatter(
        x=filtered.index,
        y=filtered["gold_usd_oz"],
        mode="lines",
        name="Gold Price (USD/oz)",
        yaxis="y2",
        line=dict(width=2),
    )
)
fig_assets.update_layout(
    template="plotly_dark",
    height=460,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="DXY Index",
    yaxis2=dict(title="Gold (USD/oz)", overlaying="y", side="right", showgrid=False),
    xaxis=dict(rangeslider=dict(visible=True)),
)
st.plotly_chart(fig_assets, use_container_width=True)

latest = filtered.iloc[-1]
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Inflation YoY", f"{latest['inflation_yoy']:.2f}%")
col2.metric("Fed Funds Rate", f"{latest['fed_funds']:.2f}%")
col3.metric("Real Rate", f"{latest['real_rate']:.2f}%")
col4.metric("DXY", f"{latest['dxy']:.2f}")
col5.metric("Gold Price", f"${latest['gold_usd_oz']:.2f}")

st.subheader("3) Portfolio Recommendation")
dxy_3m_change = filtered["dxy"].iloc[-1] - filtered["dxy"].iloc[max(0, len(filtered) - 63)]
dxy_is_strong = dxy_3m_change > 0
dxy_level = float(latest["dxy"])

if latest["real_rate"] < 0 and dxy_level < 100:
    st.success(
        "Signal: Real rate is negative and DXY is below 100. "
        "Gold is more likely to outperform -> increase gold allocation."
    )
    stock_weight, gold_weight = 25, 75
elif latest["real_rate"] > 0 and dxy_level > 100:
    st.warning(
        "Signal: Real rate is positive and DXY is above 100. "
        "Gold may face downside pressure -> reduce gold allocation."
    )
    stock_weight, gold_weight = 80, 20
else:
    st.info(
        "Signal: Mixed macro regime (or DXY near 100). "
        "Maintain a balanced allocation until the trend becomes clearer."
    )
    stock_weight, gold_weight = 50, 50

st.write(f"Suggested allocation: **Stocks {stock_weight}%** | **Gold {gold_weight}%**")

st.subheader("4) Portfolio Allocation (Gold / Stock)")
capital = st.number_input("Total capital (USD)", min_value=0.0, value=10000.0, step=100.0)

col_g, col_s = st.columns(2)
gold_alloc = col_g.number_input("Gold weight (%)", min_value=0.0, max_value=100.0, value=float(gold_weight), step=1.0)
stock_alloc = col_s.number_input("Stock weight (%)", min_value=0.0, max_value=100.0, value=float(stock_weight), step=1.0)

total_alloc = gold_alloc + stock_alloc
if abs(total_alloc - 100.0) > 1e-9:
    st.warning(f"Current total allocation is {total_alloc:.2f}%. Please adjust to 100%.")

allocation_df = pd.DataFrame(
    {
        "Asset": ["Gold", "Stock"],
        "Weight (%)": [gold_alloc, stock_alloc],
    }
)
allocation_df["Amount (USD)"] = capital * allocation_df["Weight (%)"] / 100.0

st.dataframe(
    allocation_df.style.format({"Weight (%)": "{:.2f}", "Amount (USD)": "${:,.2f}"}),
    use_container_width=True,
    hide_index=True,
)

st.markdown("**Return assumptions**")
r_col_g, r_col_s = st.columns(2)
gold_return = r_col_g.number_input("Gold return (%)", value=8.0, step=0.5)
stock_return = r_col_s.number_input("Stock return (%)", value=10.0, step=0.5)

allocation_df["Expected Return (%)"] = [gold_return, stock_return]
allocation_df["Expected Profit (USD)"] = (
    allocation_df["Amount (USD)"] * allocation_df["Expected Return (%)"] / 100.0
)

portfolio_profit = allocation_df["Expected Profit (USD)"].sum()
portfolio_return_pct = (portfolio_profit / capital * 100.0) if capital > 0 else 0.0
ending_value = capital + portfolio_profit

st.dataframe(
    allocation_df.style.format(
        {
            "Weight (%)": "{:.2f}",
            "Amount (USD)": "${:,.2f}",
            "Expected Return (%)": "{:.2f}",
            "Expected Profit (USD)": "${:,.2f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

met1, met2, met3 = st.columns(3)
met1.metric("Expected Portfolio Return", f"{portfolio_return_pct:.2f}%")
met2.metric("Expected Profit", f"${portfolio_profit:,.2f}")
met3.metric("Ending Portfolio Value", f"${ending_value:,.2f}")
