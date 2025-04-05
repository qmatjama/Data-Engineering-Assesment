
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === Load Data ===
@st.cache_data
def load_data():
    excel_path = "DE_Assesment_Results.xlsx"
    df_summary = pd.read_excel(excel_path, sheet_name="task3_summary_report")
    df_cleaned = pd.read_excel(excel_path, sheet_name="Total_cleaned_records")
    df_trend = pd.read_excel(excel_path, sheet_name="task4_volume_per_day", parse_dates=['date'])
    df_supply = pd.read_excel(excel_path, sheet_name="task4_cumulative_supply", parse_dates=['date'])
    df_top = pd.read_excel(excel_path, sheet_name="task4_top_tokens")
    return df_summary, df_cleaned, df_trend, df_supply, df_top

st.set_page_config(page_title="Token Analytics Dashboard", layout="wide")
st.title("📊 Token Distribution & Blockchain Trend Dashboard")

df_summary, df_cleaned, df_trend, df_supply, df_top = load_data()

# === Sidebar Filters ===
all_tokens = df_cleaned['token.symbol'].dropna().unique().tolist()
all_types = df_cleaned['type'].dropna().unique().tolist()
min_date = df_cleaned['timestamp'].min()
max_date = df_cleaned['timestamp'].max()
min_rate = float(df_cleaned['token.exchange_rate'].min())
max_rate = float(df_cleaned['token.exchange_rate'].max())

st.sidebar.header("🔍 Filter Transactions")
selected_token = st.sidebar.selectbox("Select Token Symbol", ["All"] + all_tokens)
selected_type = st.sidebar.selectbox("Select Transaction Type", ["All"] + all_types)
selected_date = st.sidebar.date_input("Filter by Date Range", [min_date, max_date])
rate_range = st.sidebar.slider("Token Exchange Rate", min_value=0.001, max_value=1.0, value=(min_rate, max_rate))

df_filtered = df_cleaned.copy()
if selected_token != "All":
    df_filtered = df_filtered[df_filtered['token.symbol'] == selected_token]
if selected_type != "All":
    df_filtered = df_filtered[df_filtered['type'] == selected_type]
df_filtered = df_filtered[
    (df_filtered['timestamp'].dt.date >= selected_date[0]) &
    (df_filtered['timestamp'].dt.date <= selected_date[1]) &
    (df_filtered['token.exchange_rate'] >= rate_range[0]) &
    (df_filtered['token.exchange_rate'] <= rate_range[1])
]

# === Summary Table ===
st.subheader("📦 Top Token Holders and Distribution Summary")
st.dataframe(df_summary.style.format({
    "Token Holding": "{:.6f}",
    "% of Total Holding": "{:.2f}%",
    "Tokens Sent": "{:.6f}",
    "% of Total Sent": "{:.2f}%",
    "Tokens Received": "{:.6f}",
    "% of Total Received": "{:.2f}%"
}))

# === Task 3 Charts ===
st.subheader("📈 Visual Breakdown by Address")
col1, col2, col3 = st.columns(3)

def labeled_barh(data, column, title, color):
    fig, ax = plt.subplots(figsize=(4, 3))
    bars = ax.barh(data['address'], data[column], color=color)
    ax.set_xlabel(column)
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=8)
    ax.invert_yaxis()
    for bar in bars:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.2f}',
                va='center', ha='left', fontsize=8)
    return fig

with col1:
    st.pyplot(labeled_barh(df_summary, "Token Holding", "Token Holdings", "green"))

with col2:
    st.pyplot(labeled_barh(df_summary, "Tokens Sent", "Tokens Sent", "red"))

with col3:
    st.pyplot(labeled_barh(df_summary, "Tokens Received", "Tokens Received", "blue"))

# === Task 4 Charts ===
st.subheader("📉 Task 4: Blockchain Activity Trends")
col4, col5 = st.columns(2)

with col4:
    st.markdown("##### 🔄 Daily Token Transfer Volume")
    df_t4 = df_trend.copy()
    if selected_token != "All":
        df_t4 = df_t4[df_t4['token'] == selected_token]
    fig4, ax4 = plt.subplots(figsize=(6, 3))
    for token in df_t4['token'].unique():
        token_df = df_t4[df_t4['token'] == token]
        ax4.plot(token_df['date'], token_df['daily_volume'], marker='o', label=token)
        for x, y in zip(token_df['date'], token_df['daily_volume']):
            ax4.text(x, y, f"{y:.2f}", fontsize=7)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax4.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax4.legend(fontsize=7)
    st.pyplot(fig4)

with col5:
    st.markdown("##### 📈 Cumulative Token Supply")
    df_sup = df_supply.copy()
    if selected_token != "All":
        df_sup = df_sup[df_sup['token.symbol'] == selected_token]
    fig5, ax5 = plt.subplots(figsize=(6, 3))
    for token in df_sup['token.symbol'].unique():
        token_df = df_sup[df_sup['token.symbol'] == token]
        ax5.plot(token_df['date'], token_df['cumulative_supply'], marker='o', label=token)
        for x, y in zip(token_df['date'], token_df['cumulative_supply']):
            ax5.text(x, y, f"{y:.2f}", fontsize=7)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax5.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax5.legend(fontsize=7)
    st.pyplot(fig5)

# === Top Tokens
st.subheader("🏆 Most Transferred Tokens")
fig6, ax6 = plt.subplots(figsize=(6, 3))
bars = ax6.barh(df_top['token.symbol'], df_top['total_transferred'], color='orange')
ax6.set_xlabel("Total Transferred")
ax6.set_ylabel("Token")
ax6.tick_params(labelsize=8)
ax6.invert_yaxis()
for bar in bars:
    ax6.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"{bar.get_width():.2f}", fontsize=8, va='center', ha='left')
st.pyplot(fig6)

# === Raw Cleaned Table
st.subheader("📄 Cleaned Token Transfer Records")
st.dataframe(df_filtered.reset_index(drop=True))

st.markdown("---")
st.markdown("Made with ❤️ by Qenehelo | Powered by Streamlit")
