import streamlit as st
import pandas as pd

# Thiết lập cấu hình trang
st.set_page_config(layout="wide", page_title="Marketing Dashboard Demo")

st.title("📊 Multi-platform advertising analytics dashboard (Demo)")
st.markdown("---")

# ==========================================
# 1. CẤU HÌNH THAM SỐ (Input Area)
# ==========================================
with st.sidebar:
    st.header("⚙️ Goal settings")
    
    # Cho phép người dùng tự điền các ngưỡng
    target_roas = st.number_input(
        "Expected ROAS (e.g., 4.0)", 
        min_value=0.1, 
        value=4.0, 
        step=0.1
    )
    
    target_cpa = st.number_input(
        "Expected CPA (e.g., 60000 VNĐ)", 
        min_value=1, 
        value=60000, 
        step=1000,
        format="%d"
    )
    
    operation_cost_rate = st.slider(
        "Operation cost rate (% of revenue, e.g., 50%)",
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
    st.caption("Demo mode: upload a campaign image. Campaign URLs are assumed.")

    with st.expander("Website campaign", expanded=False):
        campaign_name_website = st.text_input("Campaign name (Website)", value="Website - Always On")
        campaign_image_website = st.file_uploader(
            "Campaign image (Website)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="campaign_image_website",
        )

    with st.expander("Facebook campaign", expanded=False):
        campaign_name_facebook = st.text_input("Campaign name (Facebook)", value="Facebook - Prospecting")
        campaign_image_facebook = st.file_uploader(
            "Campaign image (Facebook)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="campaign_image_facebook",
        )

    with st.expander("TikTok campaign", expanded=False):
        campaign_name_tiktok = st.text_input("Campaign name (TikTok)", value="TikTok - Spark Ads")
        campaign_image_tiktok = st.file_uploader(
            "Campaign image (TikTok)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="campaign_image_tiktok",
        )

    # Mặc định: tự hiển thị dashboard khi mở trang
    if "run_analysis" not in st.session_state:
        st.session_state.run_analysis = True

    run_analysis = st.toggle("Show dashboard", value=st.session_state.run_analysis)
    st.session_state.run_analysis = run_analysis
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

demo_campaign_urls = {
    "Website": "https://example.com/campaigns/website-always-on",
    "Facebook": "https://example.com/campaigns/facebook-prospecting",
    "TikTok": "https://example.com/campaigns/tiktok-spark-ads",
}

campaign_assets = [
    {
        "Platform": "Website",
        "Campaign": campaign_name_website,
        "URL": demo_campaign_urls["Website"],
        "Image": campaign_image_website,
    },
    {
        "Platform": "Facebook",
        "Campaign": campaign_name_facebook,
        "URL": demo_campaign_urls["Facebook"],
        "Image": campaign_image_facebook,
    },
    {
        "Platform": "TikTok",
        "Campaign": campaign_name_tiktok,
        "URL": demo_campaign_urls["TikTok"],
        "Image": campaign_image_tiktok,
    },
]

# ==========================================
# 3. XỬ LÝ VÀ HIỂN THỊ DỮ LIỆU
# ==========================================
if run_analysis:
    st.header("SUMMARY RESULTS")

    # Tính toán các chỉ số chung
    df['ROAS'] = (df['Revenue'] / df['Spending']).round(2)
    df['CPA'] = (df['Spending'] / df['User_Reg']).round(0).astype(int)
    
    # Tính ROI (Giả định đơn giản)
    # ROI = (Lợi nhuận ròng / Tổng đầu tư) * 100
    df['Profit'] = df['Revenue'] * (1 - operation_cost_rate) - df['Spending']
    df['Total_Investment'] = df['Spending'] + (df['Revenue'] * operation_cost_rate)
    df['ROI'] = ((df['Profit'] / df['Total_Investment']) * 100).round(1)

    # Hiển thị bảng dữ liệu chính
    # Làm nổi bật các chỉ số CPA quá cao
    def highlight_cpa(s):
        return ['background-color: #ffcccc' if v > target_cpa else '' for v in s]
    
    styled_df = (
        df[['Platform', 'Spending', 'User_Reg', 'Revenue', 'ROAS', 'ROI', 'CPA']]
        .style.apply(highlight_cpa, subset=['CPA'])
        .format(
            {
                "Spending": "{:,.0f}",
                "User_Reg": "{:,.0f}",
                "Revenue": "{:,.0f}",
                "ROAS": "{:,.2f}",
                "ROI": "{:,.1f}",
                "CPA": "{:,.0f}",
            }
        )
    )
    
    st.dataframe(styled_df, use_container_width=True)

    st.markdown("---")

    st.subheader("Campaign gallery")
    cols = st.columns(3)
    for i, asset in enumerate(campaign_assets):
        with cols[i % 3]:
            st.markdown(f"**{asset['Platform']}**")
            st.write(asset["Campaign"] or "(Unnamed campaign)")
            if asset["Image"] is not None:
                st.image(asset["Image"], use_container_width=True)
            else:
                st.info("Upload an image in the sidebar to show it here.")

            if asset["URL"]:
                st.link_button("Open campaign", asset["URL"])
            else:
                st.caption("Add a Campaign URL in the sidebar to enable the link.")
    
    # ==========================================
    # 4. AI INSIGHTS & ĐỀ XUẤT HÀNH ĐỘNG
# ==========================================
    st.header("🤖 AI INSIGHTS & ACTION RECOMMENDATIONS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Smart alerts")
        alerts_found = False
        
        for index, row in df.iterrows():
            if row['ROAS'] < target_roas:
                st.error(
                    f"🚨 **{row['Platform']}**: ROAS ({row['ROAS']}) is below the target ({target_roas}). "
                    f"CPA ({row['CPA']:,} VND) is too high."
                )
                alerts_found = True
            elif row['ROAS'] > target_roas * 1.5:
                st.success(f"✅ **{row['Platform']}**: Great performance. ROAS ({row['ROAS']}) is well above target.")
                alerts_found = True

        if not alerts_found:
            st.info("No alerts found.")

    with col2:
        st.subheader("💡 Recommended actions")
        recommendations = []
        
        for index, row in df.iterrows():
            if row['ROAS'] < target_roas:
                recommendations.append(
                    f"- **{row['Platform']}**: Cut budget by 50% or pause campaigns with CPA > {target_cpa:,.0f} VND."
                )
            elif row['ROAS'] > target_roas * 1.5:
                recommendations.append(f"- **{row['Platform']}**: Increase budget by 20% to maximize new users.")
        
        if recommendations:
            for rec in recommendations:
                st.write(rec)
        else:
            st.write("Performance looks stable — no changes recommended.")

else:
    st.info("Turn on 'Show dashboard' in the sidebar to view results.")