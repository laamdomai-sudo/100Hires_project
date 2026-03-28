from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ===================== UI SETUP =====================
st.set_page_config(page_title="Macro Dashboard", layout="wide")
st.title("Macro Dashboard: CPI, Fed Rate, Real Rate, DXY, Gold")
st.caption("Offline mode: read local CSV files only (no network calls)")

# ===================== PATH CONFIG =====================
BASE_DIR = Path(__file__).resolve().parent
# Sửa dòng dưới đây: thêm / "data" để trỏ vào đúng thư mục chứa CSV
DATA_DIR = BASE_DIR / "data" 

# Debug: Hiển thị đường dẫn trên sidebar để bạn dễ kiểm tra nếu có lỗi
st.sidebar.write(f"📂 App Folder: {BASE_DIR.name}")
st.sidebar.write(f"📊 Data Folder: {DATA_DIR}")

# Đảm bảo tên file ở đây khớp 100% với tên file bạn đã up lên GitHub
REQUIRED_FILES = {
    "cpi": DATA_DIR / "cpi.csv",
    "fed_funds": DATA_DIR / "fed_funds.csv",
    "dxy": DATA_DIR / "dxy.csv",
    "gold_usd_oz": DATA_DIR / "gold.csv",
}

# ===================== DATA LOADER =====================
@st.cache_data(ttl=0)
def read_local_series(path: Path, value_col_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=[value_col_name])

    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=[value_col_name])

    columns_lower = {c.lower(): c for c in df.columns}
    date_col = columns_lower.get("date", df.columns[0])
    value_col = columns_lower.get("value", df.columns[-1])

    df[date_col] = pd.to_datetime(df[date_col].astype(str), errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    df = df.dropna(subset=[date_col, value_col])
    df = df.rename(columns={date_col: "date", value_col: value_col_name})

    return df.set_index("date").sort_index()[[value_col_name]]


def build_dataset():
    cpi = read_local_series(REQUIRED_FILES["cpi"], "cpi")
    fed = read_local_series(REQUIRED_FILES["fed_funds"], "fed_funds")
    dxy = read_local_series(REQUIRED_FILES["dxy"], "dxy")
    gold = read_local_series(REQUIRED_FILES["gold_usd_oz"], "gold_usd_oz")

    # Ghép các bảng dữ liệu lại
    df = pd.concat([cpi, fed, dxy, gold], axis=1).ffill()

    if df.empty or "cpi" not in df or "fed_funds" not in df:
        return pd.DataFrame()

    # VÌ DỮ LIỆU CỦA BẠN LÀ TỶ LỆ THEO NĂM:
    # 1. Không dùng pct_change(12) vì nó sẽ làm mất dữ liệu 12 năm đầu.
    # 2. Gán trực tiếp giá trị từ file cpi.csv vào cột inflation_yoy.
    df["inflation_yoy"] = df["cpi"] 
    
    # Tính Real Rate = Lãi suất Fed - Lạm phát
    df["real_rate"] = df["fed_funds"] - df["inflation_yoy"]

    # Không nên dùng .dropna() quá sớm nếu dữ liệu ít, 
    # dùng .fillna(0) để các biểu đồ vẫn hiện ra thay vì báo lỗi "Empty"
    return df.fillna(0)

# ===================== LOAD DATA =====================
with st.spinner("Loading data..."):
    df = build_dataset()

if df.empty:
    missing = [str(p) for p in REQUIRED_FILES.values() if not p.exists()]
    st.error("CSV data not found or invalid.")
    st.code("\n".join(missing))
    st.stop()

# ===================== FILTER =====================
timeline_start = pd.Timestamp("2000-01-01")
timeline_end = pd.Timestamp("2026-12-31")

df = df.loc[(df.index >= timeline_start) & (df.index <= timeline_end)]

if df.empty:
    st.error("No data in selected timeline.")
    st.stop()

# ===================== SIDEBAR =====================
st.sidebar.header("Configuration")

start_date = st.sidebar.date_input(
    "Start date", value=df.index.min().date()
)

end_date = st.sidebar.date_input(
    "End date", value=df.index.max().date()
)

if start_date > end_date:
    st.error("Start date must be before end date")
    st.stop()

filtered = df.loc[
    (df.index.date >= start_date) & (df.index.date <= end_date)
]

if filtered.empty:
    st.error("No data after filtering")
    st.stop()

# ===================== CHART 1: MACRO TIMELINE =====================
st.subheader("1) Inflation, Fed Rate, Real Rate")

fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered.index, y=filtered["inflation_yoy"], name="Inflation YoY", line=dict(color='#ff4b4b', width=2)))
fig.add_trace(go.Scatter(x=filtered.index, y=filtered["fed_funds"], name="Fed Rate", line=dict(color='#00d4ff', width=2)))
fig.add_trace(go.Scatter(x=filtered.index, y=filtered["real_rate"], name="Real Rate", line=dict(color='#00ff41', dash='dot')))

# Cấu hình Timeline chung
timeline_config = dict(
    rangeselector=dict(
        buttons=list([
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all", label="All")
        ]),
        bgcolor="#262730", activecolor="#ff4b4b",
    ),
    rangeslider=dict(visible=True),
    type="date"
)

fig.update_layout(
    template="plotly_dark", height=550,
    hovermode="x unified",
    xaxis=timeline_config,
    yaxis=dict(title="Percentage (%)", gridcolor="#333"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# ===================== CHART 2: ASSET TIMELINE =====================
st.subheader("2) DXY & Gold Price")

fig2 = go.Figure()
# Trục Y bên trái cho DXY
fig2.add_trace(go.Scatter(x=filtered.index, y=filtered["dxy"], name="DXY (Left)", line=dict(color='#008000')))
# Trục Y bên phải cho Gold
fig2.add_trace(go.Scatter(x=filtered.index, y=filtered["gold_usd_oz"], name="Gold (Right)", yaxis="y2", line=dict(color='#ffd700')))

fig2.update_layout(
    template="plotly_dark", height=550,
    hovermode="x unified",
    xaxis=timeline_config, # Dùng chung cấu hình timeline ở trên
    yaxis=dict(title="DXY Index", side="left", gridcolor="#333"),
    yaxis2=dict(title="Gold ($/oz)", overlaying="y", side="right", showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig2, use_container_width=True)

# ===================== METRICS =====================
latest = filtered.iloc[-1]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Inflation", f"{latest['inflation_yoy']:.2f}%")
col2.metric("Fed Rate", f"{latest['fed_funds']:.2f}%")
col3.metric("Real Rate", f"{latest['real_rate']:.2f}%")
col4.metric("DXY", f"{latest['dxy']:.2f}")
col5.metric("Gold", f"${latest['gold_usd_oz']:.2f}")

# ===================== SIGNAL =====================
st.subheader("3) Portfolio Recommendation")

if len(filtered) >= 63:
    dxy_change = filtered["dxy"].iloc[-1] - filtered["dxy"].iloc[-63]
else:
    dxy_change = 0

if latest["real_rate"] < 0 and latest["dxy"] < 100:
    st.success("Bullish Gold")
    stock_weight, gold_weight = 30, 70
elif latest["real_rate"] > 0 and latest["dxy"] > 100:
    st.warning("Bearish Gold")
    stock_weight, gold_weight = 80, 20
else:
    st.info("Neutral")
    stock_weight, gold_weight = 50, 50

st.write(f"Stocks {stock_weight}% | Gold {gold_weight}%")

# ===================== ALLOCATION & RETURN (SIDE BY SIDE) =====================
st.write("---") # Đường kẻ phân cách cho rõ ràng
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("4) Portfolio Allocation")
    capital = st.number_input("Capital ($)", value=10000.0, step=1000.0)
    
    # Sử dụng gold_weight từ phần Signal làm mặc định
    gold_alloc = st.slider("Gold %", 0, 100, int(gold_weight))
    stock_alloc = 100 - gold_alloc

    gold_amount = capital * gold_alloc / 100
    stock_amount = capital * stock_alloc / 100

    st.info(f"**Gold:** ${gold_amount:,.2f}  \n**Stock:** ${stock_amount:,.2f}")

with col_right:
    st.subheader("Expected Return")
    
    # Chia nhỏ tiếp để nhập % lợi nhuận cho gọn
    c1, c2 = st.columns(2)
    gold_return = c1.number_input("Gold return %", value=8.0, step=0.5)
    stock_return = c2.number_input("Stock return %", value=10.0, step=0.5)

    profit = (gold_amount * gold_return / 100) + (stock_amount * stock_return / 100)
    return_pct = (profit / capital * 100) if capital > 0 else 0

    # Hiển thị kết quả bằng metric cho chuyên nghiệp
    m1, m2 = st.columns(2)
    m1.metric("Total Profit", f"${profit:,.2f}")
    m2.metric("Return Rate", f"{return_pct:.2f}%")
