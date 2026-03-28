import streamlit as st
import pandas as pd

# ==========================================
# 0. THIẾT LẬP CẤU HÌNH TRANG
# ==========================================
st.set_page_config(layout="wide", page_title="Marketing Dashboard Demo")

st.title("📊 Multi-platform advertising analytics dashboard (Demo)")
st.markdown("---")

# ==========================================
# 1. CẤU HÌNH THAM SỐ (Input Area)
# ==========================================
with st.sidebar:
    st.header("⚙️ Goal settings")
    
    target_roas = st.number_input(
        "Expected ROAS (e.g., 4.0)", 
        min_value=0.1, 
        value=4.0, 
        step=0.1
    )
    
    target_cpa = st.number_input(
        "Expected CPA (VNĐ)", 
        min_value=1, 
        value=60000, 
        step=1000,
        format="%d"
    )
    
    # Tỷ lệ chi phí vận hành (COGS, Ship, Staff...)
    operation_cost_rate = st.slider(
        "Operation cost rate (% of revenue)",
        min_value=0, 
        max_value=100, 
        value=50, 
        step=5
    ) / 100.0

    st.divider()
    st.subheader("Budget (Spending)")
    spending_website = st.number_input("Website spending (VND)", min_value=0, value=10_000_000, step=500_000, format="%d")
    spending_facebook = st.number_input("Facebook spending (VND)", min_value=0, value=50_000_000, step=500_000, format="%d")
    spending_tiktok = st.number_input("TikTok spending (VND)", min_value=0, value=30_000_000, step=500_000, format="%d")
    
    st.divider()
    st.subheader("Campaign assets")
    
    with st.expander("Website campaign", expanded=False):
        campaign_name_website = st.text_input("Campaign name (Web)", value="Website - Always On")
        campaign_image_website = st.file_uploader("Image (Web)", type=["png", "jpg", "jpeg"], key="img_web")

    with st.expander("Facebook campaign", expanded=False):
        campaign_name_facebook = st.text_input("Campaign name (FB)", value="Facebook - Prospecting")
        campaign_image_facebook = st.file_uploader("Image (FB)", type=["png", "jpg", "jpeg"], key="img_fb")

    with st.expander("TikTok campaign", expanded=False):
        campaign_name_tiktok = st.text_input("Campaign name (TT)", value="TikTok - Spark Ads")
        campaign_image_tiktok = st.file_uploader("Image (TT)", type=["png", "jpg", "jpeg"], key="img_tt")

    run_analysis = st.toggle("Show dashboard", value=True)
    st.button("Refresh analysis", type="primary")

# ==========================================
# 2. DỮ LIỆU GIẢ ĐỊNH (Simulated Data)
# ==========================================
data = {
    'Platform': ['Website', 'Facebook', 'TikTok'],
    'Impressions': [100000, 1200000, 2500000],
    'Clicks': [5000, 24000, 75000],
    'Revenue': [50000000, 140000000, 135000000],
    'User_Reg': [200, 120, 600]
}

df = pd.DataFrame(data)
df["Spending"] = [spending_website, spending_facebook, spending_tiktok]

campaign_assets = [
    {"Platform": "Website", "Campaign": campaign_name_website, "Image": campaign_image_website, "URL": "https://example.com/web"},
    {"Platform": "Facebook", "Campaign": campaign_name_facebook, "Image": campaign_image_facebook, "URL": "https://facebook.com/ads"},
    {"Platform": "TikTok", "Campaign": campaign_name_tiktok, "Image": campaign_image_tiktok, "URL": "https://tiktok.com/ads"},
]

# ==========================================
# 3. XỬ LÝ VÀ HIỂN THỊ DỮ LIỆU
# ==========================================
if run_analysis:
    # --- TÍNH TOÁN CHỈ SỐ ---
    df['ROAS'] = (df['Revenue'] / df['Spending']).round(2)
    # Tránh lỗi chia cho 0 hoặc rỗng cho CPA
    df['CPA'] = (df['Spending'] / df['User_Reg']).fillna(0).replace([float('inf')], 0).astype(int)
    
    # Tính ROI chuẩn: (Doanh thu - Tổng chi phí) / Tổng chi phí
    df['Total_Cost'] = (df['Revenue'] * operation_cost_rate) + df['Spending']
    df['Profit'] = df['Revenue'] - df['Total_Cost']
    df['ROI'] = ((df['Profit'] / df['Total_Cost']) * 100).round(1)

    # --- HIỂN THỊ METRICS TỔNG QUAN ---
    st.header("📈 PERFORMANCE OVERVIEW")
    t_spend = df['Spending'].sum()
    t_rev = df['Revenue'].sum()
    t_roas = round(t_rev / t_spend, 2) if t_spend > 0 else 0
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Spending", f"{t_spend:,.0f} VNĐ")
    col_m2.metric("Total Revenue", f"{t_rev:,.0f} VNĐ")
    col_m3.metric("Avg ROAS", f"{t_roas}x", delta=f"{round(t_roas - target_roas, 2)}")

    st.markdown("---")

    # --- BẢNG DỮ LIỆU CHI TIẾT ---
    st.subheader("Platform Breakdown")
    def highlight_cpa(s):
        return ['background-color: #ffcccc' if v > target_cpa else '' for v in s]
    
    styled_df = (
        df[['Platform', 'Spending', 'User_Reg', 'Revenue', 'ROAS', 'ROI', 'CPA']]
        .style.apply(highlight_cpa, subset=['CPA'])
        .format({
            "Spending": "{:,.0f}", "User_Reg": "{:,.0f}", 
            "Revenue": "{:,.0f}", "ROAS": "{:,.2f}", 
            "ROI": "{:,.1f}%", "CPA": "{:,.0f}"
        })
    )
    st.dataframe(styled_df, use_container_width=True)

    # --- CAMPAIGN GALLERY ---
    st.markdown("---")
    st.subheader("🖼️ Campaign Gallery")
    cols = st.columns(len(campaign_assets))
    for i, asset in enumerate(campaign_assets):
        with cols[i]:
            st.markdown(f"**{asset['Platform']}**")
            st.caption(asset["Campaign"] or "Unnamed")
            if asset["Image"]:
                st.image(asset["Image"], use_container_width=True)
            else:
                st.info("No image uploaded")
            st.link_button("View Ads", asset["URL"], use_container_width=True)

    # --- AI INSIGHTS ---
    st.markdown("---")
    st.header("🤖 AI INSIGHTS & RECOMMENDATIONS")
    
    c_alert, c_rec = st.columns(2)
    
    with c_alert:
        st.subheader("Smart Alerts")
        alerts = False
        for _, row in df.iterrows():
            if row['ROAS'] < target_roas:
                st.error(f"⚠️ **{row['Platform']}**: Low ROAS ({row['ROAS']}). CPA is {row['CPA']:,} VNĐ.")
                alerts = True
            elif row['ROAS'] > target_roas * 1.5:
                st.success(f"🌟 **{row['Platform']}**: Overperforming! ROAS is {row['ROAS']}.")
                alerts = True
        if not alerts: st.write("All platforms are performing within targets.")

    with c_rec:
        st.subheader("💡 Actions")
        for _, row in df.iterrows():
            if row['ROAS'] < target_roas:
                st.write(f"👉 **{row['Platform']}**: Consider pausing or optimizing creatives to lower CPA below {target_cpa:,} VNĐ.")
            elif row['ROAS'] > target_roas * 1.5:
                st.write(f"🚀 **{row['Platform']}**: Scale budget by 15-20% to capture more volume.")

else:
    st.warning("Please enable 'Show dashboard' in the sidebar to view analysis.")
